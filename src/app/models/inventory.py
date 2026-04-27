from sqlalchemy import String, Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from .base import Base

class InventoryItem(Base):
    """
    Representa um item de estoque no banco de dados SQLAlchemy do ERP.
    """
    __tablename__ = "inventory_items"

    id: Mapped[str] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String, nullable=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    category: Mapped[str] = mapped_column(String, default="Geral", index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    reserved_quantity: Mapped[int] = mapped_column(Integer, default=0)
    min_threshold: Mapped[int] = mapped_column(Integer, default=0)
    unit_price: Mapped[float] = mapped_column(Float, default=0.0)
    location: Mapped[str] = mapped_column(String, default="Almoxarifado Principal")

    def __repr__(self) -> str:
        return f"<InventoryItem(id={self.id}, sku={self.sku}, name={self.name}, qty={self.quantity}, category={self.category})>"

class SyncHistory(Base):
    """
    Registra os eventos e relatórios de sincronização com o ERP.
    """
    __tablename__ = "sync_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    processed_count: Mapped[int] = mapped_column(Integer, default=0)
    alerts_count: Mapped[int] = mapped_column(Integer, default=0)
