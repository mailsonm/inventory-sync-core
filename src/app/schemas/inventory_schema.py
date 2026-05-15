from pydantic import BaseModel, Field
from typing import List, Optional

class InventoryItemSchema(BaseModel):
    """
    Schema Pydantic v2 para validação rigorosa de um item de estoque vindo do ERP (Odoo/SAP).
    """
    id: str = Field(..., description="Identificador único do produto no ERP")
    sku: Optional[str] = Field(default=None, description="Código SKU / Código de barras (EAN13/UPC)")
    name: str = Field(..., description="Nome do produto")
    category: Optional[str] = Field(default="Geral", description="Categoria do produto no ERP")
    quantity: int = Field(..., ge=0, description="Quantidade total física em estoque")
    reserved_quantity: int = Field(default=0, ge=0, description="Quantidade reservada para pedidos pendentes")
    min_threshold: int = Field(..., ge=0, description="Nível mínimo de segurança para alerta de estoque baixo")
    unit_price: float = Field(default=0.0, ge=0.0, description="Preço unitário do produto (R$)")
    location: Optional[str] = Field(default="Almoxarifado Principal", description="Depósito/Localização do estoque no ERP")

    @property
    def available_quantity(self) -> int:
        """Retorna a quantidade efetivamente disponível para venda (físico - reservado)."""
        return max(0, self.quantity - self.reserved_quantity)

    @property
    def total_item_value(self) -> float:
        """Calcula o valor financeiro total investido no item em estoque."""
        return round(self.quantity * self.unit_price, 2)

class InventoryListSchema(BaseModel):
    """
    Schema para a lista completa de itens de estoque.
    """
    items: List[InventoryItemSchema]

class InventoryCategorySummarySchema(BaseModel):
    """
    Schema para métricas agregadas de estoque por categoria.
    """
    category: str
    total_items: int
    total_quantity: int
    total_value: float
    alert_count: int
