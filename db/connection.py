import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import traceback
from db import db_config

class Database:
    def __init__(self):
        self.connection = None
        self.db_config = db_config.DB_CONFIG
        print(f"Database configuration loaded: {self.db_config}")

    def connect(self):
        try:
            if self.connection is None or self.connection.closed:
                print("Attempting to connect to database...")
                print(f"Using connection string: {self.db_config}")
                

                conn_str = (
                    f"dbname={self.db_config['DB_NAME']} "
                    f"user={self.db_config['DB_USER']} "
                    f"password={self.db_config['DB_PASSWORD']} "
                    f"host={self.db_config['DB_HOST']} "
                    f"port={self.db_config['DB_PORT']} "
                    "sslmode=require "
                    "keepalives=1 "
                    "keepalives_idle=30 "
                    "keepalives_interval=10 "
                    "keepalives_count=5"
                )
                
                self.connection = psycopg2.connect(conn_str)
            
            if self.ping():
                return True
            else:
                print("Connection test failed, attempting to reconnect...")
                self.connection.close()
                self.connection = None
                return self.connect()
                
        except Exception as e:
            print(f"Error connecting to database: {e}")
            print("Full traceback:")
            print(traceback.format_exc())
            if self.connection:
                self.connection.close()
            self.connection = None
            return False

    def ping(self):

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except:
            return False

    def execute_query(self, query, params=None):
        if not self.connect():
            print("Failed to establish connection")
            return None
            
        try:
            print(f"Executing query: {query}")
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                query_lower = query.strip().lower()
                if query_lower.startswith("select"):
                    result = cursor.fetchall()
                    print(f"Query result: {result}")
                    return result
                elif "returning" in query_lower:
                    result = cursor.fetchone()
                    self.connection.commit()
                    print(f"Query result: {result}")
                    return result
                else:
                    self.connection.commit()
                    print(f"Query executed successfully")
                    return cursor.rowcount
        except Exception as e:
            print(f"Database query error: {e}")
            try:
                self.connection.rollback()
            except Exception as rollback_error:
                print(f"Error during rollback: {rollback_error}")
            return None

db = Database()
