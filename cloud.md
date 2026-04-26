# Estrutura de Diretórios - ERP Integration

Esta estrutura foi desenhada para separar as preocupações de negócio das camadas de dados e infraestrutura, seguindo princípios de **Clean Architecture** e **S.O.L.I.D.**.

```text
erp_integration/
├── src/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # Entry point da aplicação
│   │   ├── models/             # Modelos de Banco de Dados (ex: SQLAlchemy/Tortoise)
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   └── inventory.py
│   │   ├── services/           # Lógica de Negócio (Interacting with models)
│   │   │   ├── __init__.py
│   │   │   ├── inventory_service.py
│   │   │   └── erp_connector.py
│   │   ├── schemas/            # DTOs/Pydantic Models para validação de entrada/saída
│   │   │   ├── __init__.py
│   │   │   └── inventory_schema.py
│   │   └── utils/              # Helpers e utilitários genéricos
│   │       ├── __init__.py
│   │       └── json_parser.py
├── tests/                      # Suite de testes (Pytest)
│   ├── __init__.py
│   ├── conftest.py             # Fixtures globais
│   ├── unit/
│   │   ├── services/
│   │   │   └── test_inventory_service.py
│   │   └── schemas/
│   │       └── test_inventory_schema.py
│   ├── integration/
├── data/                       # Arquivos de dados (JSONs de exemplo/seeds)
│   └── inventory_sample.json
├── docs/                       # Documentação Adicional
├── cloud.md                    # Detalhamento da arquitetura (este arquivo)
├── requirements.txt            # Dependências (Pydantic, Pytest, etc.)
└── pyproject.toml              # Configurações de build e ferramentas
```

## Separação de Camadas

1.  **Models (`src/app/models/`)**: Representam a estrutura de dados persistida. Devem ser anêmicos em relação a regras de negócio complexas.
2.  **Services (`src/app/services/`)**: Contêm a "verdade" do negócio. É aqui que reside a lógica de integração, cálculos de estoque e alertas.
3.  **Schemas (`src/app/schemas/`)**: Definem o contrato de dados. Usados para validar se o JSON recebido do ERP externo está correto antes de processá-lo.
4.  **Utils (`src/app/utils/`)**: Funções puras que auxiliam no processamento técnico, sem conhecimento do domínio de negócio.
