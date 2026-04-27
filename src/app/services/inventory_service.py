import json
from typing import List
from sqlalchemy.orm import Session
from pydantic import ValidationError
from ..schemas.inventory_schema import InventoryListSchema, InventoryItemSchema
from ..models.inventory import InventoryItem as DBInventoryItem, SyncHistory as DBSyncHistory

class InventoryService:
    """
    Serviço responsável por processar dados de estoque e aplicar regras de negócio.
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
            # Repassa a ValidationError do Pydantic para que os testes/quem chama possa tratar
            raise e
        except Exception as e:
            raise ValueError(f"Erro inesperado ao processar JSON: {str(e)}")

    def get_low_stock_items(self, items: List[InventoryItemSchema]) -> List[InventoryItemSchema]:
        """
        Filtra itens onde a quantidade é estritamente menor que o threshold mínimo.
        """
        return [item for item in items if item.quantity < item.min_threshold]

    def upsert_inventory(self, db: Session, items: List[InventoryItemSchema]):
        """
        Insere ou atualiza os itens de estoque no banco de dados.
        """
        for item_schema in items:
            db_item = db.query(DBInventoryItem).filter(DBInventoryItem.id == item_schema.id).first()
            
            if db_item:
                db_item.name = item_schema.name
                db_item.quantity = item_schema.quantity
                db_item.min_threshold = item_schema.min_threshold
            else:
                db_item = DBInventoryItem(
                    id=item_schema.id,
                    name=item_schema.name,
                    quantity=item_schema.quantity,
                    min_threshold=item_schema.min_threshold
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
        
        return {
            "total": total,
            "alerts": alerts,
            "out_of_stock": out_of_stock,
            "items_raw": items # Útil para o dashboard
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
