from fastapi import FastAPI, Request, Depends, UploadFile, File, HTTPException, Body
from fastapi.responses import JSONResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from .models.database import SessionLocal, init_db
from .models.inventory import InventoryItem as DBInventoryItem
from .services.inventory_service import InventoryService
from .services.erp_connector import OdooERPConnector
import os
import json

app = FastAPI(
    title="Inventory Sync Core Dashboard & ERP Connector",
    description="Core de sincronização e validação de inventário para ERPs (Odoo/SAP) desenvolvido em FastAPI, Pydantic v2 e SQLAlchemy."
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

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
    Lista todos os itens de inventário e mostra o dashboard com métricas consolidadas.
    """
    service = InventoryService()
    stats = service.get_inventory_stats(db)
    items = stats.pop("items_raw")
    history = service.get_sync_history(db)
    
    display_items = []
    for item in items:
        is_low = item.quantity < item.min_threshold
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
    Endpoint REST para excluir um item de inventário.
    """
    service = InventoryService()
    success = service.delete_item(db, item_id)
    if success:
        return {"status": "success", "message": f"Item {item_id} removido do banco de dados ERP."}
    raise HTTPException(status_code=404, detail="Item não encontrado no banco de dados.")

@app.post("/sync")
async def sync_inventory(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Recebe um arquivo JSON e atualiza o inventário no banco de dados com log de auditoria.
    """
    try:
        content = await file.read()
        json_data = content.decode("utf-8")
        
        service = InventoryService()
        inventory = service.process_json(json_data)
        service.upsert_inventory(db, inventory.items)
        
        low_stock_count = len(service.get_low_stock_items(inventory.items))
        service.log_sync_event(
            db, 
            filename=file.filename,
            processed_count=len(inventory.items),
            alerts_count=low_stock_count
        )
        
        return {"status": "success", "message": f"{len(inventory.items)} itens sincronizados e validados com sucesso."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno de processamento: {str(e)}")

@app.post("/api/inventory/sync-odoo")
def sync_odoo_payload(payload: List[Dict[str, Any]] = Body(...), db: Session = Depends(get_db)):
    """
    Endpoint para recepção de payload nativo exportado do Odoo 19 (stock.quant / product.product).
    """
    try:
        connector = OdooERPConnector()
        items_schemas = connector.import_odoo_payload(payload)
        
        service = InventoryService()
        service.upsert_inventory(db, items_schemas)
        
        low_stock_count = len(service.get_low_stock_items(items_schemas))
        service.log_sync_event(
            db,
            filename="Odoo_19_XMLRPC_Sync",
            processed_count=len(items_schemas),
            alerts_count=low_stock_count
        )
        
        return {
            "status": "success",
            "source": "Odoo 19 ERP",
            "synced_count": len(items_schemas),
            "alerts_count": low_stock_count
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar payload do Odoo: {str(e)}")

@app.get("/api/inventory/categories")
def get_categories_summary(db: Session = Depends(get_db)):
    """
    Retorna estatísticas consolidadas agrupadas por categoria de produto.
    """
    service = InventoryService()
    items = service.list_items(db)
    return service.get_category_summaries(items)

@app.get("/api/inventory/export")
def export_inventory_report(db: Session = Depends(get_db)):
    """
    Exporta o relatório financeiro e quantitativo completo de inventário em JSON.
    """
    service = InventoryService()
    items = service.list_items(db)
    low_stock = service.get_low_stock_items(items)
    
    return {
        "metadata": {
            "total_items": len(items),
            "total_value_brl": service.calculate_total_inventory_value(items),
            "low_stock_alerts": len(low_stock)
        },
        "items": [
            {
                "id": item.id,
                "sku": item.sku,
                "name": item.name,
                "category": item.category,
                "quantity": item.quantity,
                "reserved_quantity": item.reserved_quantity,
                "available_quantity": max(0, item.quantity - item.reserved_quantity),
                "min_threshold": item.min_threshold,
                "unit_price": item.unit_price,
                "total_value": round(item.quantity * item.unit_price, 2),
                "location": item.location
            }
            for item in items
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
