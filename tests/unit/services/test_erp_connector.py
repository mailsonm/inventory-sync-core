import pytest
from src.app.services.erp_connector import OdooERPConnector

def test_map_odoo_product_to_schema():
    """
    Deve converter corretamente os campos vindos do Odoo 19 (stock.quant / product.product) para o InventoryItemSchema.
    """
    connector = OdooERPConnector()
    odoo_dict = {
        "id": 101,
        "default_code": "ODOO-SKU-999",
        "name": "Dipirona 500mg Gota",
        "categ_id": [5, "Medicamentos / Analgésicos"],
        "qty_available": 45,
        "reserved_quantity": 5,
        "reordering_min_qty": 15,
        "lst_price": 12.80,
        "location_id": [2, "WH/Estoque Principal"]
    }
    
    schema = connector.map_odoo_product_to_schema(odoo_dict)
    
    assert schema.id == "101"
    assert schema.sku == "ODOO-SKU-999"
    assert schema.name == "Dipirona 500mg Gota"
    assert schema.category == "Medicamentos / Analgésicos"
    assert schema.quantity == 45
    assert schema.reserved_quantity == 5
    assert schema.available_quantity == 40
    assert schema.unit_price == 12.80
    assert schema.location == "WH/Estoque Principal"
    assert schema.total_item_value == 576.00
