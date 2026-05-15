import json
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from pydantic import ValidationError
from ..schemas.inventory_schema import InventoryListSchema, InventoryItemSchema, InventoryCategorySummarySchema
from ..models.inventory import InventoryItem as DBInventoryItem, SyncHistory as DBSyncHistory

class InventoryService:
    """
    Serviço responsável por processar dados de estoque, aplicar regras de negócio e comunicar com o ERP.
    """
    
    def process_json(self, json_data: str) -> InventoryListSchema:
        """
        Valida e processa uma string JSON representando o estoque.
        """
        try:
            data = json.loads(json_data)
            return InventoryListSchema(**data)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON malformado: {str(e)}")
        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Erro inesperado ao processar JSON: {str(e)}")

    def get_low_stock_items(self, items: List[Any]) -> List[Any]:
        """
        Filtra itens onde a quantidade é estritamente menor que o threshold mínimo.
        Funciona tanto com InventoryItemSchema quanto com DBInventoryItem.
        """
        return [item for item in items if item.quantity < item.min_threshold]

    def calculate_total_inventory_value(self, items: List[Any]) -> float:
        """
        Calcula o valor financeiro acumulado total dos itens em estoque.
        """
        total = sum((getattr(item, 'quantity', 0) * getattr(item, 'unit_price', 0.0)) for item in items)
        return round(total, 2)

    def get_category_summaries(self, items: List[Any]) -> List[InventoryCategorySummarySchema]:
        """
        Agrupa e calcula métricas financeiras e físicas de estoque por categoria.
        """
        categories: Dict[str, Dict[str, Any]] = {}

        for item in items:
            cat = getattr(item, 'category', 'Geral') or 'Geral'
            qty = getattr(item, 'quantity', 0)
            price = getattr(item, 'unit_price', 0.0)
            threshold = getattr(item, 'min_threshold', 0)

            if cat not in categories:
                categories[cat] = {
                    "category": cat,
                    "total_items": 0,
                    "total_quantity": 0,
                    "total_value": 0.0,
                    "alert_count": 0
                }

            categories[cat]["total_items"] += 1
            categories[cat]["total_quantity"] += qty
            categories[cat]["total_value"] += round(qty * price, 2)
            if qty < threshold:
                categories[cat]["alert_count"] += 1

        return [InventoryCategorySummarySchema(**data) for data in categories.values()]

    def upsert_inventory(self, db: Session, items: List[InventoryItemSchema]):
        """
        Insere ou atualiza os itens de estoque no banco de dados.
        """
        for item_schema in items:
            db_item = db.query(DBInventoryItem).filter(DBInventoryItem.id == item_schema.id).first()
            
            if db_item:
                db_item.name = item_schema.name
                db_item.sku = item_schema.sku
                db_item.category = item_schema.category or "Geral"
                db_item.quantity = item_schema.quantity
                db_item.reserved_quantity = item_schema.reserved_quantity
                db_item.min_threshold = item_schema.min_threshold
                db_item.unit_price = item_schema.unit_price
                db_item.location = item_schema.location or "Almoxarifado Principal"
            else:
                db_item = DBInventoryItem(
                    id=item_schema.id,
                    sku=item_schema.sku,
                    name=item_schema.name,
                    category=item_schema.category or "Geral",
                    quantity=item_schema.quantity,
                    reserved_quantity=item_schema.reserved_quantity,
                    min_threshold=item_schema.min_threshold,
                    unit_price=item_schema.unit_price,
                    location=item_schema.location or "Almoxarifado Principal"
                )
                db.add(db_item)
        
        db.commit()

    def list_items(self, db: Session) -> List[DBInventoryItem]:
        """
        Retorna a lista completa de itens do banco de dados.
        """
        return db.query(DBInventoryItem).all()

    def get_item(self, db: Session, item_id: str) -> DBInventoryItem:
        """
        Busca um item específico pelo ID.
        """
        return db.query(DBInventoryItem).filter(DBInventoryItem.id == item_id).first()

    def delete_item(self, db: Session, item_id: str) -> bool:
        """
        Remove um item do banco de dados. Retorna True se removido, False caso contrário.
        """
        item = self.get_item(db, item_id)
        if item:
            db.delete(item)
            db.commit()
            return True
        return False

    def get_inventory_stats(self, db: Session) -> dict:
        """
        Calcula e retorna estatísticas consolidadas do inventário.
        """
        items = self.list_items(db)
        total = len(items)
        alerts = len(self.get_low_stock_items(items))
        out_of_stock = len([i for i in items if i.quantity == 0])
        total_value = self.calculate_total_inventory_value(items)
        categories = self.get_category_summaries(items)
        
        return {
            "total": total,
            "alerts": alerts,
            "out_of_stock": out_of_stock,
            "total_value": total_value,
            "categories": categories,
            "items_raw": items
        }

    def log_sync_event(self, db: Session, filename: str, processed_count: int, alerts_count: int):
        """
        Registra um evento de sincronização no histórico.
        """
        log = DBSyncHistory(
            filename=filename,
            processed_count=processed_count,
            alerts_count=alerts_count
        )
        db.add(log)
        db.commit()

    def get_sync_history(self, db: Session, limit: int = 5) -> List[DBSyncHistory]:
        """
        Retorna os últimos eventos de sincronização.
        """
        from sqlalchemy import desc
        return db.query(DBSyncHistory).order_by(desc(DBSyncHistory.timestamp)).limit(limit).all()
