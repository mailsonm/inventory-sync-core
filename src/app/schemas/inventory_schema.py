from pydantic import BaseModel, Field
from typing import List

class InventoryItemSchema(BaseModel):
    """
    Schema para um único item de estoque vindo do ERP.
    """
    id: str = Field(..., description="Identificador único do produto")
    name: str = Field(..., description="Nome do produto")
    quantity: int = Field(..., ge=0, description="Quantidade atual em estoque")
    min_threshold: int = Field(..., ge=0, description="Nível mínimo para alerta de estoque baixo")

class InventoryListSchema(BaseModel):
    """
    Schema para a lista de itens de estoque.
    """
    items: List[InventoryItemSchema]
