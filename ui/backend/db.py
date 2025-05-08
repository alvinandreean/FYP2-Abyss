import mysql.connector
from mysql.connector import Error
from db_connect import get_db_connection

def get_connection():
    """Create and return a connection to the MySQL database"""
    return get_db_connection()

def execute_query(query, params=None, fetch=False):
    """Execute a query and optionally return results"""
    connection = get_connection()
    if not connection:
        return None
    
    cursor = connection.cursor(dictionary=True)
    result = None
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch:
            result = cursor.fetchall()
        else:
            connection.commit()
            result = cursor.lastrowid
    except Error as e:
        print(f"Error executing query: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()
    
    return result 