import mysql.connector
import pandas as pd
import streamlit as st
from utils.logger import app_logger

class MySQLHandler:
    def __init__(self):
        self.connection = None
        self.is_connected = False
    
    def connect_to_mysql(self, host, username, password, database, port=3306):
        """Connect to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=username,
                password=password,
                database=database,
                port=port
            )
            self.is_connected = True
            app_logger.info(f"Successfully connected to MySQL database: {database}")
            return True, "Connected successfully!"
        except mysql.connector.Error as e:
            app_logger.error(f"MySQL connection error: {str(e)}")
            self.is_connected = False
            return False, f"Connection failed: {str(e)}"
    
    def get_tables(self):
        """Get list of tables in the database"""
        if not self.is_connected:
            return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            cursor.close()
            return tables
        except mysql.connector.Error as e:
            app_logger.error(f"Error getting tables: {str(e)}")
            return []
    
    def get_table_info(self, table_name):
        """Get information about a specific table"""
        if not self.is_connected:
            return None
        
        try:
            cursor = self.connection.cursor()
            # Escape table name with backticks to handle spaces and special characters
            escaped_table = f"`{table_name}`"
            cursor.execute(f"DESCRIBE {escaped_table}")
            columns = cursor.fetchall()
            
            cursor.execute(f"SELECT COUNT(*) FROM {escaped_table}")
            row_count = cursor.fetchone()[0]
            
            cursor.close()
            
            return {
                "columns": columns,
                "row_count": row_count
            }
        except mysql.connector.Error as e:
            app_logger.error(f"Error getting table info for {table_name}: {str(e)}")
            return None
    
    def load_table_data(self, table_name, limit=1000):
        """Load data from a table"""
        if not self.is_connected:
            return None
        
        try:
            # Escape table name with backticks to handle spaces and special characters
            escaped_table = f"`{table_name}`"
            query = f"SELECT * FROM {escaped_table} LIMIT {limit}"
            df = pd.read_sql(query, self.connection)
            app_logger.info(f"Loaded {len(df)} rows from table {table_name}")
            return df
        except Exception as e:
            app_logger.error(f"Error loading table data from {table_name}: {str(e)}")
            return None
    
    def execute_query(self, query):
        """Execute a custom SQL query"""
        if not self.is_connected:
            return None, "Not connected to database"
        
        try:
            df = pd.read_sql(query, self.connection)
            return df, "Query executed successfully"
        except Exception as e:
            app_logger.error(f"Error executing query: {str(e)}")
            return None, f"Query error: {str(e)}"
    
    def close_connection(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            self.is_connected = False
            app_logger.info("MySQL connection closed")
