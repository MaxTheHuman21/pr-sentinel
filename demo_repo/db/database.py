"""
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

# Made with Bob
