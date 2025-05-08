import sys
from flask_bcrypt import Bcrypt
from db import execute_query, get_connection

# Initialize bcrypt
bcrypt = Bcrypt()

def reset_user_password(email, new_password):
    """Reset a user's password to a new known value"""
    print(f"Resetting password for {email}...")
    
    # Check if user exists
    users = execute_query(
        "SELECT * FROM user WHERE user_email = %s",
        (email,),
        fetch=True
    )
    
    if not users or len(users) == 0:
        print(f"No user found with email: {email}")
        return False
    
    user = users[0]
    user_id = user.get('user_id')
    print(f"User found: ID {user_id}")
    
    # Generate new password hash
    password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    print(f"Generated new password hash: {password_hash[:20]}... ({len(password_hash)} chars)")
    
    # Update the user's password
    result = execute_query(
        "UPDATE user SET user_password = %s WHERE user_id = %s",
        (password_hash, user_id)
    )
    
    if result is not None:
        print("Password updated successfully!")
        return True
    else:
        print("Failed to update password.")
        return False

def set_plaintext_password(email, new_password):
    """Set a user's password to plaintext (not recommended for production)"""
    print(f"Setting plaintext password for {email}...")
    
    # Check if user exists
    users = execute_query(
        "SELECT * FROM user WHERE user_email = %s",
        (email,),
        fetch=True
    )
    
    if not users or len(users) == 0:
        print(f"No user found with email: {email}")
        return False
    
    user = users[0]
    user_id = user.get('user_id')
    print(f"User found: ID {user_id}")
    
    # Update the user's password with plaintext
    result = execute_query(
        "UPDATE user SET user_password = %s WHERE user_id = %s",
        (new_password, user_id)
    )
    
    if result is not None:
        print("Plaintext password set successfully!")
        return True
    else:
        print("Failed to set plaintext password.")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python reset_password.py <email> <new_password> [--plaintext]")
        sys.exit(1)
    
    email = sys.argv[1]
    new_password = sys.argv[2]
    use_plaintext = "--plaintext" in sys.argv
    
    if use_plaintext:
        success = set_plaintext_password(email, new_password)
    else:
        success = reset_user_password(email, new_password)
    
    if success:
        print("\nPassword has been reset. Try logging in with the new password.")
        print("For testing, run: python test_db.py", email, new_password)
    else:
        print("\nFailed to reset password.")
    
    sys.exit(0 if success else 1) 