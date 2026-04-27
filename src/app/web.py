from fastapi import FastAPI, Request, Depends, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from .models.database import SessionLocal, init_db
from .models.inventory import InventoryItem as DBInventoryItem
from .services.inventory_service import InventoryService
import os

app = FastAPI(title="Inventory Sync Core Dashboard")

# ... (omitted static/templates setup for brevity but keeping logic) ...
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Dependency para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def read_inventory(request: Request, db: Session = Depends(get_db)):
    """
    Lista todos os itens de inventário e mostra o dashboard com histórico.
    """
    service = InventoryService()
    stats = service.get_inventory_stats(db)
    items = stats.pop("items_raw")
    history = service.get_sync_history(db)
    
    # Processar itens para o dashboard (adicionar metadados de estilo)
    display_items = []
    for item in items:
        is_low = item.quantity < item.min_threshold
        # Calcula largura da barra (máximo 100%)
        width = min(item.quantity * 5, 100)
        color = "#ef4444" if is_low else "#10b981"
        
        display_items.append({
            "obj": item,
            "width": width,
            "color": color,
            "is_low": is_low
        })
    
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "items": display_items,
            "stats": stats,
            "history": history
        }
    )

@app.delete("/items/{item_id}")
def delete_item(item_id: str, db: Session = Depends(get_db)):
    """
    Endpoint para excluir um item de inventário.
    """
    service = InventoryService()
    success = service.delete_item(db, item_id)
    if success:
        return {"status": "success", "message": f"Item {item_id} removido."}
    raise HTTPException(status_code=404, detail="Item não encontrado.")

@app.post("/sync")
async def sync_inventory(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Recebe um arquivo JSON e atualiza o inventário no banco de dados com log.
    """
    try:
        content = await file.read()
        json_data = content.decode("utf-8")
        
        service = InventoryService()
        inventory = service.process_json(json_data)
        service.upsert_inventory(db, inventory.items)
        
        # Log do evento de sincronização
        low_stock_count = len(service.get_low_stock_items(inventory.items))
        service.log_sync_event(
            db, 
            filename=file.filename,
            processed_count=len(inventory.items),
            alerts_count=low_stock_count
        )
        
        return {"status": "success", "message": f"{len(inventory.items)} itens sincronizados e registrados."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
