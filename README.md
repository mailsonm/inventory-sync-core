# inventory-sync-core 📦🚀

[🇧🇷 Português](#-português) | [🇺🇸 English](#-english) | [🇪🇸 Español](#-español)

---

## 🇧🇷 Português

**`inventory-sync-core`** é um módulo de alta performance desenvolvido em **Python 3.12+** responsável pela **sincronização, validação e persistência de inventários e estoques** entre sistemas ERPs (como **Odoo 19** e SAP) e plataformas de e-commerce/APIs.

O projeto adota princípios de **Clean Architecture** e **S.O.L.I.D.**, utilizando **Pydantic v2** para validação estrita de contratos de dados (DTOs), **SQLAlchemy 2.0** para abstração de banco de dados (SQLite/PostgreSQL) e **FastAPI** para endpoints de integração REST.

> 💬 **Nota do Desenvolvedor:**  
> *"Criado originalmente em Abril de 2026 para consolidar a integração entre conectores Odoo 19 ERP e APIs REST. Em Agosto de 2026, o projeto passou por uma revisão técnica completa de manutenção, adicionando cálculo de valor acumulado de estoque, sumarização por categoria, conector Odoo 19 nativo e suíte automatizada de testes com Pytest."*

### 🛠️ Recursos Principais
- ⚡ **Validação Estrita com Pydantic v2:** Validação automática de SKUs, preços unitários, quantidades reservadas e limites mínimos de segurança.
- 🏢 **Conector Nativo Odoo 19 (`OdooERPConnector`):** Mapeamento direto de dicionários e registros do Odoo (`stock.quant` e `product.product`).
- 📊 **Métricas Financeiras & Estoque:** Cálculo automático do valor total do inventário em R$, estoque líquido disponível (`físico - reservado`) e contagem por categorias.
- 🧪 **Testes Automatizados (Pytest):** Cobertura de testes unitários para schemas, regras de negócio e persistência ORM.
- 💻 **Interface Dupla (CLI & Dashboard FastAPI):** Execução via linha de comando para cargas em lote ou via Web Dashboard interativo.

### 🚀 Como Executar

#### 1. Instalar Dependências
```powershell
python -m pip install -r requirements.txt
```

#### 2. Executar via CLI (Carga de JSON em Lote)
```powershell
python src/app/main.py inventory_test_10.json
```

#### 3. Iniciar Dashboard Web & API REST (FastAPI)
```powershell
python src/app/web.py
# Ou via Uvicorn diretamente:
uvicorn src.app.web:app --reload --port 8000
```
Acesse o Dashboard em: `http://localhost:8000`  
Documentação Interativa Swagger API: `http://localhost:8000/docs`

#### 4. Executar Suíte de Testes Unitários (Pytest)
```powershell
python -m pytest
```

---

## 🇺🇸 English

**`inventory-sync-core`** is a high-performance Python 3.12+ core module engineered for **inventory synchronization, schema validation, and persistence** between enterprise ERPs (such as **Odoo 19**) and modern APIs.

Built following **Clean Architecture** and **S.O.L.I.D.** principles, it leverages **Pydantic v2** for strict data validation, **SQLAlchemy 2.0** for ORM persistence, and **FastAPI** for REST integration.

### Features
- ⚡ **Strict Pydantic v2 Validation:** Automatic parsing of SKUs, categories, unit prices, and reserved stock.
- 🏢 **Odoo 19 ERP Connector:** Direct mapping of Odoo `stock.quant` and `product.product` models.
- 📊 **Financial & Stock Metrics:** Real-time calculation of total inventory value, net available stock, and category summaries.
- 🧪 **Pytest Test Suite:** Full unit testing covering schemas, business logic, and database layer.

---

## 🇪🇸 Español

**`inventory-sync-core`** es un módulo core de alto rendimiento en Python 3.12+ diseñado para la **sincronización, validación y persistencia de inventario** entre ERPs corporativos (**Odoo 19**) y APIs REST.

Siguiendo principios de **Arquitectura Limpia** y **S.O.L.I.D.**, utiliza **Pydantic v2**, **SQLAlchemy 2.0** y **FastAPI**.

---

## 👤 Autor

* **Desenvolvedor:** Mailson Maia Alves  
* **GitHub:** [@mailsonm](https://github.com/mailsonm)
