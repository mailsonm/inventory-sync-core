import json
from typing import List
from sqlalchemy.orm import Session
from pydantic import ValidationError
from ..schemas.inventory_schema import InventoryListSchema, InventoryItemSchema
from ..models.inventory import InventoryItem as DBInventoryItem

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
