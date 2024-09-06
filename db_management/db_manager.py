import sqlite3
from typing import Dict, List, Any, Type
import json


class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    # def __enter__(self):
    #     self.conn = sqlite3.connect(self.db_path)
    #     self.cursor = self.conn.cursor()
    #     return self
    #
    # def __exit__(self, exc_type, exc_val, exc_tb):
    #     if self.conn:
    #         self.conn.close()

    def create_table(self, table_name: str, fields: Dict[str, str]):
        fields_str = ', '.join([f"{key} {value}" for key, value in fields.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, {fields_str})"
        self.cursor.execute(query)
        self.conn.commit()

    def insert(self, table_name: str, data: Dict[str, Any]):
        keys = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table_name} ({keys}) VALUES ({placeholders})"
        self.cursor.execute(query, list(data.values()))
        self.conn.commit()
        return self.cursor.lastrowid

    def update(self, table_name: str, id: int, data: Dict[str, Any]):
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE id = ?"
        values = list(data.values()) + [id]
        self.cursor.execute(query, values)
        self.conn.commit()

    def delete(self, table_name: str, id: int):
        query = f"DELETE FROM {table_name} WHERE id = ?"
        self.cursor.execute(query, (id,))
        self.conn.commit()

    def get(self, table_name: str, id: int) -> Dict[str, Any]:
        query = f"SELECT * FROM {table_name} WHERE id = ?"
        self.cursor.execute(query, (id,))
        row = self.cursor.fetchone()
        if row:
            columns = [desc[0] for desc in self.cursor.description]
            return dict(zip(columns, row))
        return None

    def get_all(self, table_name: str) -> List[Dict[str, Any]]:
        try:
            # Check if the table exists
            self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if self.cursor.fetchone() is None:
                print(f"Table '{table_name}' does not exist.")
                return []

            # If the table exists, proceed with the query
            query = f"SELECT * FROM {table_name}"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return []

class BaseModel:
    table_name = ""
    fields = {}

    @classmethod
    def create_table(cls, db_manager: DatabaseManager):
        db_manager.create_table(cls.table_name, cls.fields)

    @classmethod
    def create(cls, db_manager: DatabaseManager, data: Dict[str, Any]):
        return db_manager.insert(cls.table_name, data)

    @classmethod
    def get(cls, db_manager: DatabaseManager, id: int):
        return db_manager.get(cls.table_name, id)

    @classmethod
    def get_all(cls, db_manager: DatabaseManager):
        return db_manager.get_all(cls.table_name)

    @classmethod
    def update(cls, db_manager: DatabaseManager, id: int, data: Dict[str, Any]):
        db_manager.update(cls.table_name, id, data)

    @classmethod
    def delete(cls, db_manager: DatabaseManager, id: int):
        db_manager.delete(cls.table_name, id)

class DBAssistant(BaseModel):
    table_name = "assistants"
    fields = {
        "name": "TEXT",
        "description": "TEXT",
        "model": "TEXT",
        "instructions": "TEXT",
        "extra_data": "TEXT"
    }


class DBThread(BaseModel):
    table_name = "threads"
    fields = {
        "name": "TEXT",
        "oai_id": "TEXT",
        "purpose": "TEXT",
        "owner": "TEXT",
        "extra_data": "TEXT"
    }


class DBStore(BaseModel):
    table_name = "stores"
    fields = {
        "name": "TEXT",
        "description": "TEXT",
        "extra_data": "TEXT"
    }


class DBInstruction(BaseModel):
    table_name = "instructions"
    fields = {
        "content": "TEXT",
        "assistant_id": "INTEGER",
        "extra_data": "TEXT"
    }


class DBConversation(BaseModel):
    table_name = "conversations"
    fields = {
        "thread_id": "INTEGER",
        "assistant_id": "INTEGER",
        "content": "TEXT",
        "timestamp": "DATETIME DEFAULT CURRENT_TIMESTAMP",
        "extra_data": "TEXT"
    }


def initialize_database(db_path: str):
    print(f"INITIALIZE_DB, {db_path}")
    with DatabaseManager(db_path) as db:
        DBAssistant.create_table(db)
        DBThread.create_table(db)
        DBStore.create_table(db)
        DBInstruction.create_table(db)
        DBConversation.create_table(db)


# # Example usage
# if __name__ == "__main__":
#     db_path = "wonders_and_worries.db"
#     initialize_database(db_path)
#
#     with DatabaseManager(db_path) as db:
#         # Create an assistant
#         assistant_id = Assistant.create(db, {
#             "name": "Test Assistant",
#             "description": "A test assistant",
#             "model": "gpt-3.5-turbo",
#             "instructions": "Some instructions",
#             "extra_data": json.dumps({"key": "value"})
#         })
#
#         # Get the assistant
#         assistant = Assistant.get(db, assistant_id)
#         print("Created assistant:", assistant)
#
#         # Update the assistant
#         Assistant.update(db, assistant_id, {"name": "Updated Assistant"})
#
#         # Get all assistants
#         assistants = Assistant.get_all(db)
#         print("All assistants:", assistants)
#
#         # Delete the assistant
#         Assistant.delete(db, assistant_id)
#
#         # Similar operations can be performed for Thread, Store, Instruction, and Conversation