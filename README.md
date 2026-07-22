# Project 3 - Database Integration
This project upgrades the todo API to use a **PostgreSQL** database instead of in-memory JSON storage. Connects the backend using **FastAPI** with a database to store and retrieve data.

---
## About the Project

### Files
*   **`main.py`**: FastAPI routes and request validation
*   **`database.py`**: PostgreSQL connection and CRUD helpers
*   **`schema.sql`**: Table definition for the todo database
*   **`requirements.txt`**: Python dependencies

## Database Setup
* Create a PostgreSQL database in DBeaver.
* Executed `schema.sql` queries in the dbeaver to create todo table and function to change update time.
* Add the name, username, and password in `database.py` to connect them togther.

## How to Set Up and Run

### 1. Install Dependencies
Open your terminal in the project folder and run:
```
# Create a virtual environment
python -m venv venv
# Activate it:
.\venv\Scripts\activate.bat
# Install the packages
pip install -r requirements.txt
```

### 2. Start the Server
Start the development server using:
```
uvicorn main:app --reload
```
The server will start at: **`http://127.0.0.1:8000`**

### 3. Open Interactive API Docs
Go to **`http://127.0.0.1:8000/docs`** in your browser to interactively test all endpoints.




