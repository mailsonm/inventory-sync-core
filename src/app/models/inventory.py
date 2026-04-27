from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
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

class SyncHistory(Base):
    """
    Tracks inventory synchronization events.
    """
    __tablename__ = "sync_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    processed_count: Mapped[int] = mapped_column(Integer, default=0)
    alerts_count: Mapped[int] = mapped_column(Integer, default=0)
