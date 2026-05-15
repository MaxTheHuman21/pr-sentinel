**User:**

<task>
Escribe una clase Database en db/database.py. Debe tener métodos get(query) y save(data) simulados. Usa tipos de Python 3.11+. Incluye manejo básico de excepciones.
</task>
<environment_details>
# VSCode Visible Files
../bob_task_4.md

# VSCode Open Tabs
demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md,demo_repo/api/orders.py,demo_repo/middleware/auth_middleware.py,../bob_task_4.md,bob_sessions_demo/bob_task_3_API_Users.md,bob_sessions_demo/bob_task_2_API_Orders.md,demo_repo/api/users.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-15T18:00:11.171Z
User time zone: America/Mexico_City, UTC-6:00

# Current Cost
$0.00

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>


# Current Workspace Directory (/home/yamato/pr-sentinel) Files
.env.example
.gitignore
ARCHITECTURE.md
github_client.py
LICENSE
llm_reasoner.py
README.md
repo_analyzer.py
report_formatter.py
requirements.txt
sentinel.py
bob_sessions_demo/
bob_sessions_demo/bob_task_1_ADR002.png
bob_sessions_demo/bob_task_1.md
bob_sessions_demo/bob_task_2_API_Orders.md
bob_sessions_demo/bob_task_2_API_Orders.png
bob_sessions_demo/bob_task_3_API_Users.md
bob_sessions_demo/bob_task_3_API_Users.png
demo_repo/
demo_repo/api/
demo_repo/api/orders.py
demo_repo/api/products.py
demo_repo/api/users.py
demo_repo/db/
demo_repo/db/database.py
demo_repo/docs/
demo_repo/docs/adr/
demo_repo/docs/adr/ADR-001-estructura-modular.md
demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md
demo_repo/docs/adr/ADR-003-manejo-de-errores.md
demo_repo/middleware/
demo_repo/middleware/auth_middleware.py
demo_repo/services/
demo_repo/services/order_service.py
demo_repo/services/user_service.py
tests/
tests/test_github_client.py
tests/test_llm_reasoner.py
tests/test_repo_analyzer.py
tests/test_report_formatter.py
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

I'll create a Database class in `db/database.py` with simulated `get` and `save` methods, using Python 3.11+ type hints and basic exception handling.

Let me first check if the file already exists:

<read_file>
<args>
<file>
<path>demo_repo/db/database.py</path>
</file>
</args>
</read_file>

---

**User:**

[read_file for 'demo_repo/db/database.py'. Reading multiple files at once is more efficient for the LLM. If other files are relevant to your current task, please read them simultaneously.] Result:
<files>
<file><path>demo_repo/db/database.py</path>
<content/><notice>File is empty</notice>
</file>
</files>
<environment_details>
# VSCode Visible Files
demo_repo/db/database.py

# VSCode Open Tabs
demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md,demo_repo/api/orders.py,demo_repo/middleware/auth_middleware.py,demo_repo/db/database.py,bob_sessions_demo/bob_task_3_API_Users.md,bob_sessions_demo/bob_task_2_API_Orders.md,demo_repo/api/users.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-15T18:00:36.175Z
User time zone: America/Mexico_City, UTC-6:00

# Current Cost
$0.01

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>


# Current Workspace Directory (/home/yamato/pr-sentinel) Files
.env.example
.gitignore
ARCHITECTURE.md
github_client.py
LICENSE
llm_reasoner.py
README.md
repo_analyzer.py
report_formatter.py
requirements.txt
sentinel.py
bob_sessions_demo/
bob_sessions_demo/bob_task_1_ADR002.png
bob_sessions_demo/bob_task_1.md
bob_sessions_demo/bob_task_2_API_Orders.md
bob_sessions_demo/bob_task_2_API_Orders.png
bob_sessions_demo/bob_task_3_API_Users.md
bob_sessions_demo/bob_task_3_API_Users.png
demo_repo/
demo_repo/api/
demo_repo/api/orders.py
demo_repo/api/products.py
demo_repo/api/users.py
demo_repo/db/
demo_repo/db/database.py
demo_repo/docs/
demo_repo/docs/adr/
demo_repo/docs/adr/ADR-001-estructura-modular.md
demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md
demo_repo/docs/adr/ADR-003-manejo-de-errores.md
demo_repo/middleware/
demo_repo/middleware/auth_middleware.py
demo_repo/services/
demo_repo/services/order_service.py
demo_repo/services/user_service.py
tests/
tests/test_github_client.py
tests/test_llm_reasoner.py
tests/test_repo_analyzer.py
tests/test_report_formatter.py
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

Now I'll write the Database class with Python 3.11+ type hints, simulated methods, and basic exception handling:

<write_to_file>
<path>demo_repo/db/database.py</path>
<content>"""
Database module with simulated operations.

This module provides a Database class with simulated get and save operations
for demonstration purposes.
"""

from typing import Any


class DatabaseError(Exception):
    """Base exception for database operations."""
    pass


class QueryError(DatabaseError):
    """Exception raised when a query fails."""
    pass


class SaveError(DatabaseError):
    """Exception raised when a save operation fails."""
    pass


class Database:
    """
    Simulated database class with basic operations.
    
    This class provides simulated database operations for testing and
    demonstration purposes. It includes basic exception handling.
    """
    
    def __init__(self, connection_string: str | None = None) -> None:
        """
        Initialize the database connection.
        
        Args:
            connection_string: Optional connection string for the database.
        """
        self.connection_string = connection_string or "simulated://localhost"
        self._data: dict[str, Any] = {}
        self._connected = False
    
    def connect(self) -> None:
        """Establish a simulated database connection."""
        if not self._connected:
            self._connected = True
            print(f"Connected to database: {self.connection_string}")
    
    def disconnect(self) -> None:
        """Close the simulated database connection."""
        if self._connected:
            self._connected = False
            print("Disconnected from database")
    
    def get(self, query: str) -> dict[str, Any] | list[dict[str, Any]] | None:
        """
        Execute a simulated query to retrieve data.
        
        Args:
            query: The query string to execute.
            
        Returns:
            Retrieved data as a dictionary, list of dictionaries, or None if not found.
            
        Raises:
            QueryError: If the query execution fails.
            DatabaseError: If the database is not connected.
        """
        if not self._connected:
            raise DatabaseError("Database is not connected. Call connect() first.")
        
        if not query or not isinstance(query, str):
            raise QueryError("Invalid query: query must be a non-empty string")
        
        try:
            # Simulate query execution
            print(f"Executing query: {query}")
            
            # Simulate retrieving data based on query
            if query.lower().startswith("select"):
                # Return simulated data
                return [
                    {"id": 1, "name": "Sample Record 1"},
                    {"id": 2, "name": "Sample Record 2"}
                ]
            elif "id" in query.lower():
                # Return single record
                return {"id": 1, "name": "Sample Record", "status": "active"}
            else:
                return None
                
        except Exception as e:
            raise QueryError(f"Query execution failed: {str(e)}") from e
    
    def save(self, data: dict[str, Any]) -> bool:
        """
        Save data to the simulated database.
        
        Args:
            data: Dictionary containing the data to save.
            
        Returns:
            True if the save operation was successful.
            
        Raises:
            SaveError: If the save operation fails.
            DatabaseError: If the database is not connected.
        """
        if not self._connected:
            raise DatabaseError("Database is not connected. Call connect() first.")
        
        if not data or not isinstance(data, dict):
            raise SaveError("Invalid data: data must be a non-empty dictionary")
        
        try:
            # Simulate save operation
            print(f"Saving data: {data}")
            
            # Store data in simulated storage
            record_id = data.get("id", len(self._data) + 1)
            self._data[str(record_id)] = data.copy()
            
            print(f"Data saved successfully with ID: {record_id}")
            return True
            
        except Exception as e:
            raise SaveError(f"Save operation failed: {str(e)}") from e
    
    def __enter__(self) -> "Database":
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type: type[BaseException] | None, 
                 exc_val: BaseException | None, 
                 exc_tb: Any) -> None:
        """Context manager exit."""
        self.disconnect()
</content>
<line_count>139</line_count>
</write_to_file>

---

**User:**

[write_to_file for 'demo_repo/db/database.py'] Result:
<file_write_result>
<path>demo_repo/db/database.py</path>
<operation>modified</operation>
<notice>
<i>You do not need to re-read the file, as you have seen all changes</i>
<i>Proceed with the task using these changes as the new baseline.</i>
</notice>
</file_write_result>

<environment_details>
# VSCode Visible Files
demo_repo/db/database.py

# VSCode Open Tabs
demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md,demo_repo/api/orders.py,demo_repo/middleware/auth_middleware.py,demo_repo/db/database.py,bob_sessions_demo/bob_task_3_API_Users.md,bob_sessions_demo/bob_task_2_API_Orders.md,demo_repo/api/users.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-15T18:03:12.537Z
User time zone: America/Mexico_City, UTC-6:00

# Current Cost
$0.02

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

<attempt_completion>
<result>
Created Database class in demo_repo/db/database.py with:

**Features:**
- Python 3.11+ type hints (using `|` union syntax, `dict[str, Any]`)
- Simulated `get(query)` method that returns data based on query patterns
- Simulated `save(data)` method that stores data in internal dictionary
- Custom exception hierarchy: `DatabaseError`, `QueryError`, `SaveError`
- Connection management with `connect()` and `disconnect()` methods
- Context manager support (`__enter__`/`__exit__`) for automatic connection handling
- Comprehensive docstrings for all methods
- Basic validation and error handling for both operations

**Exception Handling:**
- Validates database connection state
- Validates input parameters (non-empty strings for queries, non-empty dicts for data)
- Wraps exceptions with descriptive error messages
- Uses exception chaining with `from e` for better debugging

The class is ready for use in simulated/testing scenarios.
</result>
</attempt_completion>

