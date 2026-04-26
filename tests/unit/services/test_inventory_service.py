import pytest
import json
from pydantic import ValidationError
from src.app.services.inventory_service import InventoryService
from src.app.schemas.inventory_schema import InventoryItemSchema

def test_process_inventory_malformed_json():
    """
    Deve falhar se o arquivo JSON estiver malformado (erro de sintaxe).
    """
    service = InventoryService()
    malformed_json_content = '{"items": [{"id": 1, "name": "Produto A" ]}' # Erro de sintaxe (falta colchete)
    
    with pytest.raises(ValueError, match="JSON malformado"):
        service.process_json(malformed_json_content)

def test_inventory_schema_validation_failure():
    """
    Deve falhar se o JSON for válido sintaticamente, mas não seguir o Schema (ex: tipos errados).
    """
    service = InventoryService()
    invalid_data_json = json.dumps({
        "items": [{"id": "p1", "name": "Parafuso", "quantity": "muito", "min_threshold": 10}]
    }) # quantity deve ser int
    
    with pytest.raises(ValidationError):
        service.process_json(invalid_data_json)

def test_low_stock_alert_logic():
    """
    Deve retornar corretamente apenas os itens cujo estoque está abaixo do 'threshold'.
    """
    service = InventoryService()
    items = [
        InventoryItemSchema(id="p1", name="Parafuso", quantity=5, min_threshold=10),   # Alerta
        InventoryItemSchema(id="p2", name="Porca", quantity=20, min_threshold=10),     # OK
        InventoryItemSchema(id="p3", name="Arruela", quantity=2, min_threshold=5)      # Alerta
    ]
    
    results = service.get_low_stock_items(items)
    
    expected_ids = ["p1", "p3"]
    assert [item.id for item in results] == expected_ids
    assert len(results) == 2

def test_inventory_stats_calculation():
    """
    Deve calcular as estatísticas corretamente com base nos itens.
    """
    from src.app.models.database import SessionLocal, init_db
    from src.app.models.inventory import InventoryItem as DBItem
    
    init_db()
    db = SessionLocal()
    service = InventoryService()
    
    # Limpa DB para o teste
    db.query(DBItem).delete()
    
    # Prepara dados
    items = [
        InventoryItemSchema(id="t1", name="Test 1", quantity=0, min_threshold=5),  # Alerta + Zerado
        InventoryItemSchema(id="t2", name="Test 2", quantity=10, min_threshold=5)   # OK
    ]
    service.upsert_inventory(db, items)
    
    stats = service.get_inventory_stats(db)
    
    assert stats["total"] == 2
    assert stats["alerts"] == 1
    assert stats["out_of_stock"] == 1
    assert len(stats["items_raw"]) == 2
    
    # Teste delete
    service.delete_item(db, "t1")
    assert service.get_item(db, "t1") is None
    assert service.get_inventory_stats(db)["total"] == 1
    
    db.close()
