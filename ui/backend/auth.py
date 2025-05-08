from flask_bcrypt import Bcrypt
import jwt  # Using PyJWT instead of jwt package
import datetime
import os
from dotenv import load_dotenv
from db import execute_query

# Load environment variables
load_dotenv()
bcrypt = Bcrypt()
JWT_SECRET = os.getenv('JWT_SECRET')

def register_user(email, password, user_fname, user_lname):
    """Register a new user with their email, password, first name and last name"""
    # Check if email already exists
    existing_user = execute_query(
        "SELECT * FROM user WHERE user_email = %s",
        (email,),
        fetch=True
    )
    
    if existing_user:
        return {"success": False, "message": "Email already registered"}
    
    # Hash the password
    try:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        print(f"Generated bcrypt hash: {hashed_password[:20]}...")
    except Exception as e:
        print(f"Error hashing password with bcrypt: {str(e)}")
        print("Falling back to plaintext password (not recommended for production)")
        hashed_password = password
    
    # Insert the new user
    user_id = execute_query(
        "INSERT INTO user (user_email, user_password, user_fname, user_lname) VALUES (%s, %s, %s, %s)",
        (email, hashed_password, user_fname, user_lname)
    )
    
    if user_id:
        return {"success": True, "message": "Registration successful"}
    else:
        return {"success": False, "message": "Registration failed"}

def login_user(email, password):
    """Authenticate a user and return a JWT token"""
    # Get user by email
    users = execute_query(
        "SELECT * FROM user WHERE user_email = %s",
        (email,),
        fetch=True
    )
    
    print(f"Login attempt for email: {email}")
    
    if not users or len(users) == 0:
        print(f"No user found with email: {email}")
        return {"success": False, "message": "Invalid email or password"}
    
    user = users[0]
    print(f"User found: {user['user_id']}, checking password...")
    
    # Print the password hash for debugging (remove in production)
    password_hash = user.get('user_password', 'No password hash found')
    password_type = type(password_hash).__name__
    print(f"Password hash type: {password_type}")
    print(f"Password hash from DB (first 20 chars): {str(password_hash)[:20] if password_hash else 'None'}")
    
    # Check if the password hash is stored correctly
    if 'user_password' not in user or not user['user_password']:
        print("User record missing password hash!")
        return {"success": False, "message": "Account error, please contact support"}
    
    # Check password - first try direct comparison for plaintext passwords
    try:
        # Try direct comparison first (in case passwords are stored as plaintext)
        if user['user_password'] == password:
            print("Login successful with plaintext password match")
            
            try:
                # Generate JWT token
                payload = {
                    'user_id': user['user_id'],
                    'email': user['user_email'],
                    'first_name': user['user_fname'],
                    'last_name': user['user_lname'],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
                }
                token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
                
                # For PyJWT < 2.0.0, token is bytes and needs to be decoded to string
                if isinstance(token, bytes):
                    token = token.decode('utf-8')
                
                # For debugging
                print(f"Generated token type: {type(token).__name__}")
                print(f"JWT encode successful")
                
                return {
                    "success": True,
                    "message": "Login successful",
                    "token": token,
                    "user": {
                        "id": user['user_id'],
                        "email": user['user_email'],
                        "first_name": user['user_fname'],
                        "last_name": user['user_lname']
                    }
                }
            except Exception as jwt_error:
                print(f"Error generating JWT token: {str(jwt_error)}")
                return {"success": False, "message": "Login error, please try again"}
        
        # Then try bcrypt check
        try:
            password_matches = bcrypt.check_password_hash(user['user_password'], password)
            print(f"Bcrypt password check result: {password_matches}")
            
            if password_matches:
                try:
                    # Generate JWT token
                    payload = {
                        'user_id': user['user_id'],
                        'email': user['user_email'],
                        'first_name': user['user_fname'],
                        'last_name': user['user_lname'],
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
                    }
                    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
                    
                    # For PyJWT < 2.0.0, token is bytes and needs to be decoded to string
                    if isinstance(token, bytes):
                        token = token.decode('utf-8')
                    
                    # For debugging
                    print(f"Generated token type: {type(token).__name__}")
                    print(f"JWT encode successful")
                    
                    return {
                        "success": True,
                        "message": "Login successful",
                        "token": token,
                        "user": {
                            "id": user['user_id'],
                            "email": user['user_email'],
                            "first_name": user['user_fname'],
                            "last_name": user['user_lname']
                        }
                    }
                except Exception as jwt_error:
                    print(f"Error generating JWT token: {str(jwt_error)}")
                    return {"success": False, "message": "Login error, please try again"}
        except Exception as bcrypt_error:
            print(f"Error in bcrypt check: {str(bcrypt_error)}")
            
        # If we get here, both password checks failed
        return {"success": False, "message": "Invalid email or password"}
    except Exception as e:
        print(f"Error checking password: {str(e)}")
        return {"success": False, "message": "Login error, please try again"}

def verify_token(token):
    """Verify a JWT token and return the user information"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return {"success": True, "user": payload}
    except jwt.ExpiredSignatureError:
        return {"success": False, "message": "Token expired"}
    except jwt.InvalidTokenError:
        return {"success": False, "message": "Invalid token"}
    except Exception as e:
        print(f"Error verifying token: {str(e)}")
        return {"success": False, "message": "Invalid token"} 