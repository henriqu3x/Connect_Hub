import os
import uuid
from datetime import datetime
from db.connection import db

def get_file_extension(filename):
    return os.path.splitext(filename)[1].lower()

def get_mime_type(extension):
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }
    return mime_types.get(extension, 'application/octet-stream')

def save_file(file_path, user_id):
    try:
        with open(file_path, 'rb') as f:
            file_data = f.read()

        file_name = os.path.basename(file_path)
        file_ext = get_file_extension(file_name)
        mime_type = get_mime_type(file_ext)

        query = """
            INSERT INTO arquivos (nome_arquivo, tipo_mime, dados, usuario_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        result = db.execute_query(query, (file_name, mime_type, file_data, user_id))
        
        if result:
            return result['id']
        return None
        
    except Exception as e:
        print(f"Erro ao salvar arquivo: {e}")
        return None

def get_file(file_id):
    try:
        query = """
            SELECT id, nome_arquivo, tipo_mime, dados, data_upload, usuario_id
            FROM arquivos
            WHERE id = %s
        """
        result = db.execute_query(query, (file_id,))
        
        if result and len(result) > 0:
            return result[0]
        return None
        
    except Exception as e:
        print(f"Erro ao recuperar arquivo: {e}")
        return None

def delete_file(file_id, user_id):
    try:
        query_check = "SELECT id FROM arquivos WHERE id = %s AND usuario_id = %s"
        result = db.execute_query(query_check, (file_id, user_id))
        
        if not result:
            return False

        query_delete = "DELETE FROM arquivos WHERE id = %s"
        result = db.execute_query(query_delete, (file_id,))
        
        return result is not None
        
    except Exception as e:
        print(f"Erro ao remover arquivo: {e}")
        return False
