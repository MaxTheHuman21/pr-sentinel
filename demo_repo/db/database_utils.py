"""
Database Utilities
Provides utility functions for database operations and maintenance.

RESOURCE MANAGEMENT ISSUE: This module has connection leaks and doesn't use
context managers properly, which can cause resource exhaustion in production.
"""

import sqlite3
import time
from typing import List, Dict, Any, Optional


# ISSUE: Global connection variable - not thread-safe and can cause leaks
db_connection = None
db_cursor = None


def get_database_connection(db_path: str = "app.db"):
    """
    Get a database connection.
    
    ISSUE: Opens connection but doesn't ensure it's closed properly.
    Should use context manager (with statement) instead.
    """
    global db_connection
    
    # ISSUE: Opens connection without proper cleanup mechanism
    db_connection = sqlite3.connect(db_path)
    db_connection.row_factory = sqlite3.Row
    
    return db_connection


def execute_query(query: str, params: tuple = ()) -> List[Dict]:
    """
    Execute a database query.
    
    ISSUE: Opens connection but doesn't close it, causing resource leak.
    SUGGESTION: Use context manager to ensure proper cleanup.
    """
    # ISSUE: Opens connection without closing it
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    
    # ISSUE: Connection is never closed!
    # Should use: conn.close() or better yet, use 'with' statement
    
    return [dict(row) for row in results]


def execute_batch_insert(table: str, records: List[Dict]) -> int:
    """
    Insert multiple records into a table.
    
    ISSUE: Opens connection, performs operations, but doesn't close properly.
    """
    # ISSUE: Connection opened but not guaranteed to close
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    
    inserted_count = 0
    
    try:
        for record in records:
            columns = ', '.join(record.keys())
            placeholders = ', '.join(['?' for _ in record])
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            cursor.execute(query, tuple(record.values()))
            inserted_count += 1
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        print(f"Error during batch insert: {e}")
    
    # ISSUE: Connection not closed - resource leak!
    # If an exception occurs before this point, connection stays open
    
    return inserted_count


def update_records(table: str, updates: Dict, condition: str) -> int:
    """
    Update records in a table.
    
    ISSUE: Another example of connection not being closed properly.
    """
    # ISSUE: Opens connection without proper cleanup
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    
    set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
    query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
    
    cursor.execute(query, tuple(updates.values()))
    conn.commit()
    
    affected_rows = cursor.rowcount
    
    # ISSUE: Connection left open - memory leak in long-running applications
    
    return affected_rows


def get_table_statistics(table_name: str) -> Dict[str, Any]:
    """
    Get statistics about a database table.
    
    ISSUE: Opens connection, performs multiple queries, never closes.
    """
    # ISSUE: Connection opened without proper resource management
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    
    stats = {}
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
    stats['row_count'] = cursor.fetchone()[0]
    
    # Get table info
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    stats['column_count'] = len(columns)
    stats['columns'] = [col[1] for col in columns]
    
    # Get index info
    cursor.execute(f"PRAGMA index_list({table_name})")
    indexes = cursor.fetchall()
    stats['index_count'] = len(indexes)
    
    # ISSUE: Connection never closed - will accumulate in memory
    
    return stats


def vacuum_database(db_path: str = "app.db") -> bool:
    """
    Vacuum the database to reclaim space.
    
    ISSUE: Opens connection for maintenance but doesn't close it.
    """
    try:
        # ISSUE: Connection opened without cleanup
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("VACUUM")
        conn.commit()
        
        # ISSUE: Connection not closed
        
        return True
        
    except Exception as e:
        print(f"Error vacuuming database: {e}")
        return False


def analyze_database(db_path: str = "app.db") -> Dict[str, Any]:
    """
    Analyze database and gather statistics.
    
    ISSUE: Opens connection, runs analysis, but leaves it open.
    """
    # ISSUE: No context manager, connection will leak
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    analysis = {
        'timestamp': time.time(),
        'tables': []
    }
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        
        # Get row count for each table
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        
        analysis['tables'].append({
            'name': table_name,
            'rows': row_count
        })
    
    # Run ANALYZE command
    cursor.execute("ANALYZE")
    conn.commit()
    
    # ISSUE: Connection left open - resource leak
    
    return analysis


def backup_table(source_table: str, backup_table: str) -> bool:
    """
    Create a backup of a table.
    
    ISSUE: Opens connection for backup operation but doesn't close it.
    """
    try:
        # ISSUE: Connection without proper cleanup
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        
        # Drop backup table if exists
        cursor.execute(f"DROP TABLE IF EXISTS {backup_table}")
        
        # Create backup
        cursor.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM {source_table}")
        
        conn.commit()
        
        # ISSUE: Connection not closed
        
        return True
        
    except Exception as e:
        print(f"Error backing up table: {e}")
        return False


class DatabaseMigration:
    """
    Handle database migrations.
    
    ISSUE: Class that opens connections but doesn't manage them properly.
    """
    
    def __init__(self, db_path: str = "app.db"):
        self.db_path = db_path
        # ISSUE: Opens connection in __init__ without __del__ or context manager
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
    
    def create_migration_table(self):
        """Create table to track migrations."""
        # ISSUE: Uses instance connection that may never be closed
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
    
    def apply_migration(self, version: str, sql: str):
        """
        Apply a database migration.
        
        ISSUE: Uses instance connection without proper cleanup.
        """
        try:
            # Execute migration SQL
            self.cursor.executescript(sql)
            
            # Record migration
            self.cursor.execute(
                "INSERT INTO migrations (version) VALUES (?)",
                (version,)
            )
            
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            print(f"Migration failed: {e}")
            return False
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migrations."""
        # ISSUE: Uses instance connection
        self.cursor.execute("SELECT version FROM migrations ORDER BY id")
        return [row[0] for row in self.cursor.fetchall()]
    
    # ISSUE: No __del__ or close() method to cleanup connection
    # Connection will remain open until garbage collection


# Module-level function with connection leak
def optimize_database_indexes(db_path: str = "app.db") -> Dict[str, int]:
    """
    Optimize database indexes.
    
    ISSUE: Opens connection, performs optimization, but doesn't close.
    """
    # ISSUE: Connection opened without context manager
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    results = {
        'reindexed': 0,
        'analyzed': 0
    }
    
    # Get all indexes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indexes = cursor.fetchall()
    
    # Reindex each one
    for index in indexes:
        index_name = index[0]
        cursor.execute(f"REINDEX {index_name}")
        results['reindexed'] += 1
    
    # Analyze tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"ANALYZE {table_name}")
        results['analyzed'] += 1
    
    conn.commit()
    
    # ISSUE: Connection never closed - resource leak!
    
    return results

# Made with Bob
