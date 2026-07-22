import os
from typing import Any, Dict, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "todo")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "dbms")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )

def initialize_database() -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS todos (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'in_progress', 'completed')),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION set_updated_at()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
                """
            )
            cursor.execute(
                """
                DROP TRIGGER IF EXISTS todos_updated_at ON todos;
                CREATE TRIGGER todos_updated_at
                BEFORE UPDATE ON todos
                FOR EACH ROW
                EXECUTE FUNCTION set_updated_at();
                """
            )
            connection.commit()
# converts row into python dictionary for 
def _row_to_todo(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "status": row["status"],
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
    }
# create a new todo item
def create_todo(title: str, description: str, status: str) -> Dict[str, Any]:
    with get_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                INSERT INTO todos (title, description, status)
                VALUES (%s, %s, %s)
                RETURNING id, title, description, status, created_at, updated_at
                """,
                (title, description, status),
            )
            row = cursor.fetchone()
            connection.commit()
            return _row_to_todo(row)
# read all todo items
def get_todos() -> List[Dict[str, Any]]:
    with get_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT id, title, description, status, created_at, updated_at FROM todos ORDER BY id"
            )
            rows = cursor.fetchall()
            return [_row_to_todo(row) for row in rows]
# read a todo item by its ID
def get_todo(todo_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT id, title, description, status, created_at, updated_at FROM todos WHERE id = %s",
                (todo_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return _row_to_todo(row)
# update a todo item by its ID
def update_todo(
    todo_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    fields = []
    values: List[Any] = []

    if title is not None:
        fields.append("title = %s")
        values.append(title)

    if description is not None:
        fields.append("description = %s")
        values.append(description)

    if status is not None:
        fields.append("status = %s")
        values.append(status)

    if not fields:
        return get_todo(todo_id)

    values.extend([todo_id])

    with get_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                f"UPDATE todos SET {', '.join(fields)} WHERE id = %s RETURNING id, title, description, status, created_at, updated_at",
                values,
            )
            row = cursor.fetchone()
            connection.commit()
            if row is None:
                return None
            return _row_to_todo(row)
# delete a todo item by its ID
def delete_todo(todo_id: int) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
            connection.commit()
            return cursor.rowcount > 0

