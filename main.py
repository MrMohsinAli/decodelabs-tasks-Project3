from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
import database

app = FastAPI(
    title="Database Integration with ToDo List API",
    description="A simple todo list API that persists data to a PostgreSQL database.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, description="The title of the item.")
    description: str = Field(default="", description="Detailed description of the item.")
    status: str = Field(default="pending", description="The current status of the item.")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Title must not be empty.')
        return v.strip()

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed_statuses = {'pending', 'in_progress', 'completed'}
        if v not in allowed_statuses:
            raise ValueError('Status must be one of: pending, in_progress, completed.')
        return v

class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, description="The updated title.")
    description: Optional[str] = Field(None, description="The updated description.")
    status: Optional[str] = Field(None, description="The updated status.")

    @field_validator('title')
    @classmethod
    def validate_title_update(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError('Title must not be empty.')
            return v.strip()
        return v

    @field_validator('status')
    @classmethod
    def validate_status_update(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed_statuses = {'pending', 'in_progress', 'completed'}
            if v not in allowed_statuses:
                raise ValueError('Status must be one of: pending, in_progress, completed.')
        return v

class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)
    
@app.on_event("startup")
def startup_event() -> None:
    database.initialize_database()

@app.get("/")
def read_root():
    """Welcome endpoint pointing to the API documentation."""
    return {
        "message": "Welcome to the ToDo List API!",
        "documentation": "/docs"
    }

@app.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate):
    """Create a new To-Do item."""
    return database.create_todo(todo.title, todo.description, todo.status)

@app.get("/todos", response_model=List[TodoResponse])
def read_todos(skip: int = 0, limit: int = 100):
    """Retrieve multiple To-Do items."""
    todos = database.get_todos()
    return todos[skip : skip + limit]

@app.get("/todos/{todo_id}", response_model=TodoResponse)
def read_todo(todo_id: int):
    """Retrieve a specific To-Do item by ID."""
    todo = database.get_todo(todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"To-Do item with ID {todo_id} not found."
        )
    return todo

@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo_update: TodoUpdate):
    """Update a To-Do item (allows updating title, description, or status)."""
    todo = database.update_todo(
        todo_id,
        title=todo_update.title,
        description=todo_update.description,
        status=todo_update.status,
    )
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ToDo item with id {todo_id} not found."
        )
    return todo

@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int):
    """Delete a To-Do item."""
    deleted = database.delete_todo(todo_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ToDo item with id {todo_id} not found."
        )
    return None

