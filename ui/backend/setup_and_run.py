import os
import sys
from dotenv import load_dotenv
from db_connect import get_db_connection

load_dotenv()

def check_env_vars():
    """Check if all required environment variables are set"""
    required_vars = ['DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD', 'DB_NAME', 'JWT_SECRET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
        print("\nPlease create a .env file in the backend directory with the following format:")
        print("""
# Railway MySQL Connection
DB_HOST=your-railway-mysql-host.railway.app
DB_PORT=your-railway-mysql-port
DB_USER=your-railway-mysql-username
DB_PASSWORD=your-railway-mysql-password
DB_NAME=your-railway-mysql-database-name
JWT_SECRET=your-secret-key-for-jwt
        """)
        return False
    return True

def test_db_connection():
    """Test the connection to the database"""
    print("Testing connection to Railway MySQL...")
    conn = get_db_connection()
    if conn:
        print("✅ Successfully connected to the database!")
        conn.close()
        return True
    else:
        print("❌ Failed to connect to the database. Please check your connection details.")
        return False

def main():
    """Main function to set up and run the application"""
    print("=== Railway MySQL Setup and Run Script ===")
    
    # Step 1: Check environment variables
    if not check_env_vars():
        return False
    
    # Step 2: Test database connection
    if not test_db_connection():
        return False
    
    # Step 3: Run the application
    print("\nStarting the Flask application...")
    try:
        import app
        app.app.run(debug=True)
        return True
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 