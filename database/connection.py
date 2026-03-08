"""
Database Connection Utility

Provides connection management and helper functions for database operations.
"""

import os
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages database connections and connection pooling"""
    
    _connection_pool: Optional[pool.SimpleConnectionPool] = None
    
    @classmethod
    def initialize_pool(cls, connection_string: Optional[str] = None, 
                       minconn: int = 1, maxconn: int = 10):
        """
        Initialize connection pool
        
        Args:
            connection_string: PostgreSQL connection string
            minconn: Minimum number of connections in pool
            maxconn: Maximum number of connections in pool
        """
        if cls._connection_pool is not None:
            logger.warning("Connection pool already initialized")
            return
        
        conn_string = connection_string or os.environ.get(
            'DATABASE_URL', 
            'postgresql://localhost/themed_animation'
        )
        
        try:
            cls._connection_pool = pool.SimpleConnectionPool(
                minconn,
                maxconn,
                conn_string
            )
            logger.info("Database connection pool initialized")
        except psycopg2.Error as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise
    
    @classmethod
    def close_pool(cls):
        """Close all connections in the pool"""
        if cls._connection_pool is not None:
            cls._connection_pool.closeall()
            cls._connection_pool = None
            logger.info("Database connection pool closed")
    
    @classmethod
    @contextmanager
    def get_connection(cls):
        """
        Get a connection from the pool
        
        Usage:
            with DatabaseConnection.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM users")
        """
        if cls._connection_pool is None:
            cls.initialize_pool()
        
        conn = cls._connection_pool.getconn()
        try:
            yield conn
        finally:
            cls._connection_pool.putconn(conn)
    
    @classmethod
    @contextmanager
    def get_cursor(cls, commit: bool = False):
        """
        Get a cursor with automatic connection management
        
        Args:
            commit: Whether to commit after cursor operations
            
        Usage:
            with DatabaseConnection.get_cursor(commit=True) as cur:
                cur.execute("INSERT INTO users (email) VALUES (%s)", ('user@example.com',))
        """
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                if commit:
                    conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Database operation failed: {e}")
                raise
            finally:
                cursor.close()


class DatabaseHelper:
    """Helper functions for common database operations"""
    
    @staticmethod
    def execute_query(query: str, params: tuple = None, fetch: str = 'all') -> Any:
        """
        Execute a SELECT query
        
        Args:
            query: SQL query string
            params: Query parameters
            fetch: 'all', 'one', or 'none'
            
        Returns:
            Query results based on fetch parameter
        """
        with DatabaseConnection.get_cursor() as cur:
            cur.execute(query, params)
            
            if fetch == 'all':
                return cur.fetchall()
            elif fetch == 'one':
                return cur.fetchone()
            else:
                return None
    
    @staticmethod
    def execute_insert(query: str, params: tuple = None, returning: bool = True) -> Any:
        """
        Execute an INSERT query
        
        Args:
            query: SQL INSERT query
            params: Query parameters
            returning: Whether to return the inserted row ID
            
        Returns:
            Inserted row ID if returning=True, else None
        """
        with DatabaseConnection.get_cursor(commit=True) as cur:
            cur.execute(query, params)
            
            if returning:
                return cur.fetchone()[0] if cur.rowcount > 0 else None
            return None
    
    @staticmethod
    def execute_update(query: str, params: tuple = None) -> int:
        """
        Execute an UPDATE query
        
        Args:
            query: SQL UPDATE query
            params: Query parameters
            
        Returns:
            Number of rows affected
        """
        with DatabaseConnection.get_cursor(commit=True) as cur:
            cur.execute(query, params)
            return cur.rowcount
    
    @staticmethod
    def execute_delete(query: str, params: tuple = None) -> int:
        """
        Execute a DELETE query
        
        Args:
            query: SQL DELETE query
            params: Query parameters
            
        Returns:
            Number of rows deleted
        """
        with DatabaseConnection.get_cursor(commit=True) as cur:
            cur.execute(query, params)
            return cur.rowcount
    
    @staticmethod
    def table_exists(table_name: str) -> bool:
        """
        Check if a table exists
        
        Args:
            table_name: Name of the table
            
        Returns:
            True if table exists, False otherwise
        """
        query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = %s
            )
        """
        result = DatabaseHelper.execute_query(query, (table_name,), fetch='one')
        return result[0] if result else False
    
    @staticmethod
    def get_table_count(table_name: str) -> int:
        """
        Get row count for a table
        
        Args:
            table_name: Name of the table
            
        Returns:
            Number of rows in the table
        """
        query = f"SELECT COUNT(*) FROM {table_name}"
        result = DatabaseHelper.execute_query(query, fetch='one')
        return result[0] if result else 0


# Example usage functions
def example_usage():
    """Example usage of database utilities"""
    
    # Initialize connection pool
    DatabaseConnection.initialize_pool()
    
    # Using get_connection
    with DatabaseConnection.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM themes")
            themes = cur.fetchall()
            print(f"Found {len(themes)} themes")
    
    # Using get_cursor
    with DatabaseConnection.get_cursor(commit=True) as cur:
        cur.execute(
            "INSERT INTO users (email) VALUES (%s) RETURNING id",
            ('user@example.com',)
        )
        user_id = cur.fetchone()[0]
        print(f"Created user with ID: {user_id}")
    
    # Using helper functions
    themes = DatabaseHelper.execute_query("SELECT * FROM themes")
    print(f"Themes: {themes}")
    
    user_count = DatabaseHelper.get_table_count('users')
    print(f"Total users: {user_count}")
    
    # Close pool when done
    DatabaseConnection.close_pool()


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Run example
    example_usage()
