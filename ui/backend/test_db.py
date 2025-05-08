import os
import sys
from dotenv import load_dotenv
from db_connect import get_db_connection
from db import execute_query
from flask_bcrypt import Bcrypt

# Load environment variables
load_dotenv()
bcrypt = Bcrypt()

def test_connection():
    """Test the connection to the Railway database"""
    conn = get_db_connection()
    if conn:
        print("Connected to the database successfully!")
        conn.close()
        return True
    else:
        print("Failed to connect to the database.")
        return False

def check_user_table():
    """Check if the user table exists and its structure"""
    result = execute_query(
        "SHOW TABLES LIKE 'user'",
        fetch=True
    )
    
    if result:
        print("'user' table exists.")
        
        # Check table structure
        columns = execute_query(
            "SHOW COLUMNS FROM user",
            fetch=True
        )
        
        print("\nTable structure:")
        for col in columns:
            print(f"- {col['Field']}: {col['Type']}, Null: {col['Null']}, Key: {col['Key']}, Default: {col['Default']}")
        
        # Check if there are any users in the table
        users = execute_query(
            "SELECT * FROM user LIMIT 5",
            fetch=True
        )
        
        if users:
            print(f"\nFound {len(users)} users in the table:")
            for user in users:
                # Show user data but mask the password partially
                password_display = "None"
                if user.get('user_password'):
                    password_type = type(user['user_password']).__name__
                    password_len = len(str(user['user_password']))
                    password_preview = str(user['user_password'])[:10]
                    password_display = f"{password_preview}... ({password_type}, {password_len} chars)"
                
                print(f"- ID: {user.get('user_id')}")
                print(f"  Email: {user.get('user_email')}")
                print(f"  Name: {user.get('user_fname')} {user.get('user_lname')}")
                print(f"  Password: {password_display}")
                print()
        else:
            print("\nNo users found in the table.")
    else:
        print("'user' table does not exist.")

def test_specific_login(email, password):
    """Test login with specific credentials"""
    print(f"\nTesting login for email: {email}")
    
    # Get user by email
    users = execute_query(
        "SELECT * FROM user WHERE user_email = %s",
        (email,),
        fetch=True
    )
    
    if not users or len(users) == 0:
        print(f"No user found with email: {email}")
        return False
    
    user = users[0]
    print(f"User found: {user.get('user_id')}")
    
    # Print the password hash for debugging
    password_hash = user.get('user_password', 'No password hash found')
    password_type = type(password_hash).__name__
    print(f"Password hash type: {password_type}")
    print(f"Password hash from DB (first 20 chars): {str(password_hash)[:20] if password_hash else 'None'}")
    
    # Try direct comparison
    if user.get('user_password') == password:
        print("✅ Plaintext password match SUCCESSFUL")
    else:
        print("❌ Plaintext password match FAILED")
    
    # Try bcrypt comparison if possible
    try:
        if bcrypt.check_password_hash(user.get('user_password', ''), password):
            print("✅ Bcrypt password match SUCCESSFUL")
        else:
            print("❌ Bcrypt password match FAILED")
    except Exception as e:
        print(f"❌ Bcrypt check error: {str(e)}")

# Run the tests
if __name__ == "__main__":
    print("=== Database Test Tool ===")
    print("Testing database connection...")
    if not test_connection():
        sys.exit(1)
    
    check_user_table()
    
    # Test specific login if email is provided
    if len(sys.argv) >= 3:
        email = sys.argv[1]
        password = sys.argv[2]
        test_specific_login(email, password)
    else:
        print("\nTo test a specific login, run:")
        print("python test_db.py <email> <password>")
    
    print("\nDone.") 