from typing import List, Dict, Any
from ..schemas.inventory_schema import InventoryItemSchema

class OdooERPConnector:
    """
    Conector simulado de integração entre o Odoo 19 ERP (stock.quant / product.product)
    e o core FastAPI Pydantic do inventory-sync-core.
    """
    def __init__(self, host: str = "http://localhost:8069", db: str = "odoo_db"):
        self.host = host
        self.db = db

    def map_odoo_product_to_schema(self, odoo_dict: Dict[str, Any]) -> InventoryItemSchema:
        """
        Mapeia a estrutura nativa de dicionário de produtos do Odoo 19 para o InventoryItemSchema.
        Exemplo de campos Odoo: default_code (SKU), name, qty_available, reserved_quantity, lst_price.
        """
        return InventoryItemSchema(
            id=str(odoo_dict.get("id", "0")),
            sku=odoo_dict.get("default_code") or odoo_dict.get("barcode"),
            name=odoo_dict.get("name", "Produto Odoo Sem Nome"),
            category=odoo_dict.get("categ_id", ["Geral", "Geral"])[1] if isinstance(odoo_dict.get("categ_id"), (list, tuple)) else str(odoo_dict.get("categ_id", "Geral")),
            quantity=int(odoo_dict.get("qty_available", 0)),
            reserved_quantity=int(odoo_dict.get("reserved_quantity", 0)),
            min_threshold=int(odoo_dict.get("reordering_min_qty", 5)),
            unit_price=float(odoo_dict.get("lst_price") or odoo_dict.get("standard_price") or 0.0),
            location=odoo_dict.get("location_id", ["Almoxarifado Odoo", "Almoxarifado Odoo"])[1] if isinstance(odoo_dict.get("location_id"), (list, tuple)) else "Almoxarifado Principal"
        )

    def import_odoo_payload(self, odoo_payload: List[Dict[str, Any]]) -> List[InventoryItemSchema]:
        """
        Converte uma lista de registros exportados do Odoo 19 para o formato validado pelo Pydantic.
        """
        return [self.map_odoo_product_to_schema(item) for item in odoo_payload]
