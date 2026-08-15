# Arquitetura Técnica - Inventory Sync Core (FastAPI & Odoo 19)

O **`inventory-sync-core`** foi arquitetado seguindo os princípios de **Clean Architecture** e **S.O.L.I.D.** para garantir desacoplamento entre as regras de negócio de estoque e as camadas de persistência e apresentação.

```text
src/
└── app/
    ├── main.py                 # CLI Entrypoint para lote de arquivos JSON
    ├── web.py                  # API REST FastAPI & Web Dashboard (Jinja2)
    ├── models/                 # Camada de Persistência (SQLAlchemy ORM 2.0)
    │   ├── base.py             # Base Declarativa do ORM
    │   ├── database.py         # Conexão e Gerenciador de Sessão SQLite/PostgreSQL
    │   └── inventory.py        # Entidades DB (InventoryItem, SyncHistory)
    ├── schemas/                # Camada de Validação & DTOs (Pydantic v2)
    │   └── inventory_schema.py # Schemas rigorosos de entrada/saída
    └── services/               # Camada de Negócio (Domain Logic & ERP Connectors)
        ├── inventory_service.py # Lógica de conciliação, métricas e alertas
        └── erp_connector.py    # Conector de mapeamento nativo Odoo 19
```

---

## 🏛️ Princípios de Design Aplicados

1. **Single Responsibility Principle (SRP):**
   - `InventoryItemSchema` cuida exclusivamente da validação de tipos e garantias numéricas.
   - `InventoryService` encapsula os cálculos financeiros e lógica de sincronização.
   - `OdooERPConnector` abstrai a conversão dos dados específicos da estrutura de modelos do Odoo 19 (`stock.quant`, `product.product`).

2. **Dependency Inversion Principle (DIP):**
   - As rotas do FastAPI utilizam Injeção de Dependência (`Depends(get_db)`) para receber sessões do SQLAlchemy, facilitando o isolamento por mocks em testes unitários.

3. **Data Transfer Objects (DTOs) com Pydantic v2:**
   - Garantia de imutabilidade e conversão segura de tipos de entrada antes que qualquer dado atinja a camada de banco de dados.
