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
    malformed_json_content = '{"items": [{"id": 1, "name": "Produto A" ]}'
    
    with pytest.raises(ValueError, match="JSON malformado"):
        service.process_json(malformed_json_content)

def test_inventory_schema_validation_failure():
    """
    Deve falhar se o JSON for válido sintaticamente, mas não seguir o Schema (ex: quantidade negativa).
    """
    service = InventoryService()
    invalid_data_json = json.dumps({
        "items": [{"id": "p1", "name": "Parafuso", "quantity": -5, "min_threshold": 10}]
    })
    
    with pytest.raises(ValidationError):
        service.process_json(invalid_data_json)

def test_low_stock_alert_logic():
    """
    Deve retornar corretamente apenas os itens cujo estoque está abaixo do 'threshold'.
    """
    service = InventoryService()
    items = [
        InventoryItemSchema(id="p1", name="Parafuso", quantity=5, min_threshold=10),
        InventoryItemSchema(id="p2", name="Porca", quantity=20, min_threshold=10),
        InventoryItemSchema(id="p3", name="Arruela", quantity=2, min_threshold=5)
    ]
    
    results = service.get_low_stock_items(items)
    
    expected_ids = ["p1", "p3"]
    assert [item.id for item in results] == expected_ids
    assert len(results) == 2

def test_calculate_total_inventory_value():
    """
    Deve calcular corretamente o valor financeiro total do estoque investido.
    """
    service = InventoryService()
    items = [
        InventoryItemSchema(id="p1", name="Item 1", quantity=10, min_threshold=5, unit_price=15.50),
        InventoryItemSchema(id="p2", name="Item 2", quantity=4, min_threshold=2, unit_price=100.00)
    ]
    
    total_val = service.calculate_total_inventory_value(items)
    # (10 * 15.50) + (4 * 100.00) = 155.00 + 400.00 = 555.00
    assert total_val == 555.00

def test_category_summaries_calculation():
    """
    Deve resumir e agrupar métricas de estoque por categoria.
    """
    service = InventoryService()
    items = [
        InventoryItemSchema(id="p1", name="Remédio A", category="Medicamentos", quantity=10, min_threshold=5, unit_price=20.0),
        InventoryItemSchema(id="p2", name="Remédio B", category="Medicamentos", quantity=2, min_threshold=10, unit_price=30.0),
        InventoryItemSchema(id="p3", name="Luva M", category="Materiais", quantity=50, min_threshold=20, unit_price=5.0)
    ]
    
    summaries = service.get_category_summaries(items)
    assert len(summaries) == 2
    
    med_summary = next(s for s in summaries if s.category == "Medicamentos")
    assert med_summary.total_items == 2
    assert med_summary.total_quantity == 12
    assert med_summary.total_value == 260.00
    assert med_summary.alert_count == 1

def test_inventory_stats_calculation():
    """
    Deve calcular as estatísticas corretamente no banco de dados SQLite.
    """
    from src.app.models.database import SessionLocal, init_db
    from src.app.models.inventory import InventoryItem as DBItem
    
    init_db()
    db = SessionLocal()
    service = InventoryService()
    
    db.query(DBItem).delete()
    
    items = [
        InventoryItemSchema(id="t1", name="Test 1", category="Cat A", quantity=0, min_threshold=5, unit_price=10.0),
        InventoryItemSchema(id="t2", name="Test 2", category="Cat B", quantity=10, min_threshold=5, unit_price=25.0)
    ]
    service.upsert_inventory(db, items)
    
    stats = service.get_inventory_stats(db)
    
    assert stats["total"] == 2
    assert stats["alerts"] == 1
    assert stats["out_of_stock"] == 1
    assert stats["total_value"] == 250.0
    assert len(stats["items_raw"]) == 2
    
    service.delete_item(db, "t1")
    assert service.get_item(db, "t1") is None
    assert service.get_inventory_stats(db)["total"] == 1
    
    db.close()
