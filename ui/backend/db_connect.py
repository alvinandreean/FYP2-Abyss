import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Load environment variables from .env file
load_dotenv()

def get_db_connection():
    """
    Create a connection to the MySQL database hosted on Railway
    Returns the connection object if successful, None otherwise
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        
        if connection.is_connected():
            print("Successfully connected to Railway MySQL database!")
            return connection
        
    except Error as e:
        print(f"Error connecting to Railway MySQL: {e}")
        return None

# Test connection when this file is run directly
if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        conn.close()
        print("Connection closed.")
