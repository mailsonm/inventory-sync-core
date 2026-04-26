from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Nome do arquivo de banco de dados
DATABASE_URL = "sqlite:///erp.db"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Necessário apenas para SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Cria as tabelas no banco de dados se elas não existirem.
    """
    from .base import Base
    # Importar modelos aqui para garantir que sejam registrados no Base
    from .inventory import InventoryItem
    Base.metadata.create_all(bind=engine)
