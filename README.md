# inventory-sync-core

[🇧🇷 Português] | [🇪🇸 Español] | [🇺🇸 English]

## Descrição / Descripción / Description

**PT-BR:** Core de sincronização e validação de inventário para sistemas ERP. Desenvolvido em Python, utiliza **Pydantic** para validação robusta e **SQLAlchemy** para persistência de dados.

**ES:** Core de sincronización y validación de inventario para sistemas ERP. Desarrollado en Python, utiliza **Pydantic** para una validación robusta y **SQLAlchemy** para la persistencia de datos.

**EN:** Core inventory synchronization and validation for ERP systems. Built with Python, it uses **Pydantic** for robust validation and **SQLAlchemy** for data persistence.

## Funcionalidades / Funcionalidades / Features

- ✅ **PT-BR:** Validação de Schema com Pydantic / **ES:** Validación de Schema con Pydantic / **EN:** Schema Validation with Pydantic.
- ✅ **PT-BR:** Processamento de JSON de inventário / **ES:** Procesamiento de JSON de inventario / **EN:** Inventory JSON processing.
- ✅ **PT-BR:** Alertas de estoque baixo / **ES:** Alertas de stock bajo / **EN:** Low stock alerts.
- ✅ **PT-BR:** Persistência automatizada (Upsert) / **ES:** Persistencia automatizada (Upsert) / **EN:** Automated persistence (Upsert).

## Como Rodar / Cómo Ejecutar / How to Run

1.  **Ambiente virtual / Entorno virtual / Virtual env:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
2.  **Dependências / Dependencias / Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Testes / Pruebas / Tests:**
    ```bash
    pytest
    ```

## Estrutura / Estructura / Structure

- `src/app/models/`: Database models (SQLAlchemy).
- `src/app/schemas/`: Schema definitions (Pydantic).
- `src/app/services/`: Business logic.
- `tests/`: Automated tests.
