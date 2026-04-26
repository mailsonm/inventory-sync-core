from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class InventoryItem(Base):
    """
    Represents a stock item in the database.
    """
    __tablename__ = "inventory_items"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(index=True)
    quantity: Mapped[int] = mapped_column(default=0)
    min_threshold: Mapped[int] = mapped_column(default=0)

    def __repr__(self) -> str:
        return f"<InventoryItem(id={self.id}, name={self.name}, qty={self.quantity})>"
