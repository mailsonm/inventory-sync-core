import argparse
import sys
import os
from src.app.services.inventory_service import InventoryService
from src.app.models.database import init_db, SessionLocal

def main():
    parser = argparse.ArgumentParser(description="ERP Inventory Integration CLI")
    parser.add_argument(
        "file", 
        help="Caminho para o arquivo JSON de estoque"
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Erro: Arquivo '{args.file}' não encontrado.")
        sys.exit(1)
        
    try:
        # Inicializa o banco de dados (cria tabelas se não existirem)
        init_db()
        
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        service = InventoryService()
        inventory = service.process_json(content)
        
        # Persistência no Banco de Dados
        db = SessionLocal()
        try:
            service.upsert_inventory(db, inventory.items)
            print("Sucesso: Dados persistidos no banco de dados.")
        finally:
            db.close()
            
        # Relatório de Estoque Baixo
        low_stock_items = service.get_low_stock_items(inventory.items)
        
        print("\n" + "="*40)
        print("   RELATÓRIO DE INTEGRAÇÃO DE ESTOQUE")
        print("="*40)
        print(f"Itens processados: {len(inventory.items)}")
        print(f"Alertas de estoque baixo: {len(low_stock_items)}")
        print("-" * 40)
        
        if low_stock_items:
            print(f"{'ID':<10} | {'PRODUTO':<20} | {'QTD':<5} | {'MÍN'}")
            print("-" * 40)
            for item in low_stock_items:
                print(f"{item.id:<10} | {item.name[:20]:<20} | {item.quantity:<5} | {item.min_threshold}")
        else:
            print("Nenhum item com estoque baixo encontrado.")
            
        print("="*40 + "\n")
        
    except ValueError as e:
        print(f"Erro de Validação: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Erro Inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
