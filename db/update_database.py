import sys
import os
from connection import db

def run_sql_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_commands = f.read()
            

        commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip()]
        
        for command in commands:
            if command:
                print(f"Executando: {command[:100]}...")
                result = db.execute_query(command)
                if result is None:
                    print(f"Erro ao executar o comando: {command[:100]}...")
                    return False
        return True
    except Exception as e:
        print(f"Erro ao executar o arquivo SQL: {e}")
        return False

if __name__ == "__main__":
    print("Atualizando esquema do banco de dados...")
    

    script_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file = os.path.join(script_dir, "update_schema.sql")
    
    if not os.path.exists(sql_file):
        print(f"Arquivo SQL não encontrado: {sql_file}")
        sys.exit(1)
    
    if run_sql_file(sql_file):
        print("Esquema do banco de dados atualizado com sucesso!")
    else:
        print("Ocorreu um erro ao atualizar o esquema do banco de dados.")
        sys.exit(1)
