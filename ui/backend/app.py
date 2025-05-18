from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from fgsm import FGSM  # your FGSM class
from auth import register_user, login_user, verify_token
from flask_bcrypt import Bcrypt
from db import execute_query, get_connection
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

# Initialize database connection (without creating tables)
def init_db():
    connection = get_connection()
    if not connection:
        print("Failed to connect to database for initialization")
        return
    
    # Test the database connection
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        print("Database connection successful")
    except Exception as e:
        print(f"Database connection test failed: {e}")
    finally:
        connection.close()

# Authentication routes
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user_fname = data.get('user_fname')
    user_lname = data.get('user_lname')
    
    if not email or not password or not user_fname or not user_lname:
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    
    result = register_user(email, password, user_fname, user_lname)
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    print(f"Login request received for email: {email}")
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required'}), 400
    
    result = login_user(email, password)
    
    if result['success']:
        print(f"Login successful for user: {email}")
        return jsonify(result), 200
    else:
        print(f"Login failed for user: {email}, reason: {result.get('message', 'Unknown')}")
        return jsonify(result), 401

@app.route('/verify-token', methods=['POST'])
def verify():
    data = request.json
    token = data.get('token')
    
    if not token:
        return jsonify({'success': False, 'message': 'Token is required'}), 400
    
    result = verify_token(token)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 401

@app.route('/available-images', methods=['GET'])
def get_available_images():
    try:
        # Fetch all images from the database
        images = execute_query(
            "SELECT image_filename, image_label, image_url FROM railway.image",
            fetch=True
        )
        
        # Format the response
        image_list = []
        for image in images:
            image_list.append({
                'filename': image['image_filename'],
                'label': image['image_label'],
                'url': image['image_url']
            })
        
        return jsonify({'success': True, 'images': image_list}), 200
    except Exception as e:
        print(f"Error fetching images: {str(e)}")
        return jsonify({'success': False, 'message': f'Error fetching images: {str(e)}'}), 500

@app.route('/attack', methods=['POST'])
def attack():
    if 'image' not in request.files or 'model' not in request.form:
        return jsonify({'error': 'No image or model provided'}), 400

    model_name = request.form['model']  # e.g. "mobilenet_v2"
    epsilon_value = float(request.form.get('epsilon', 0.05))
    auto_tune = request.form.get('autoTune', 'false').lower() == 'true'

    # Initialize FGSM
    fgsm = FGSM(epsilon=epsilon_value, model_name=model_name)

    # Save uploaded image to temp
    image_file = request.files['image']
    image_path = "temp_image.jpg"
    image_file.save(image_path)

    # Attack
    if auto_tune:
        results = fgsm.auto_tune_attack(image_path)
    else:
        fgsm.epsilon = epsilon_value
        results = fgsm.attack(image_path)

    if results:
        # Optionally attach the model name used, so it can be displayed
        results["model_used"] = model_name
        
        # We're skipping saving attack history to avoid permission issues
        
        return jsonify(results)
    else:
        return jsonify({'error': 'Attack failed'}), 500

@app.route('/attack-from-url', methods=['POST'])
def attack_from_url():
    data = request.json
    if not data or 'imageUrl' not in data or 'model' not in data:
        return jsonify({'error': 'No image URL or model provided'}), 400

    model_name = data['model']
    epsilon_value = float(data.get('epsilon', 0.05))
    auto_tune = data.get('autoTune', False)
    image_url = data['imageUrl']
    
    # Initialize FGSM
    fgsm = FGSM(epsilon=epsilon_value, model_name=model_name)

    try:
        # Download image from URL
        import requests
        from io import BytesIO
        from PIL import Image
        
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))
        image_path = "temp_image.jpg"
        image.save(image_path)
        
        # Attack
        if auto_tune:
            results = fgsm.auto_tune_attack(image_path)
        else:
            fgsm.epsilon = epsilon_value
            results = fgsm.attack(image_path)

        if results:
            # Attach the model name used
            results["model_used"] = model_name
            
            # Save attack to history if user is authenticated
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                token_result = verify_token(token)
                
                if token_result['success']:
                    user_id = token_result['user']['user_id']
                    
                    # Save attack to history
                    execute_query(
                        """
                        INSERT INTO attack_history 
                        (user_id, model_used, epsilon_used, orig_class, orig_conf, adv_class, adv_conf)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            user_id, 
                            model_name, 
                            results['epsilon_used'],
                            results['orig_class'],
                            results['orig_conf'],
                            results['adv_class'],
                            results['adv_conf']
                        )
                    )
            
            return jsonify(results)
        else:
            return jsonify({'error': 'Attack failed'}), 500
    except Exception as e:
        return jsonify({'error': f'Error processing attack: {str(e)}'}), 500

@app.route('/history', methods=['GET'])
def get_history():
    # Get user ID from token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    token = auth_header.split(' ')[1]
    token_result = verify_token(token)
    
    if not token_result['success']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    user_id = token_result['user']['user_id']
    
    # Try to get attack history, but don't fail if table doesn't exist
    try:
        history = execute_query(
            "SELECT * FROM attack_history WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,),
            fetch=True
        )
        return jsonify({'success': True, 'history': history}), 200
    except Exception as e:
        print(f"Error fetching history: {e}")
        return jsonify({'success': True, 'history': [], 'message': 'History feature unavailable'}), 200

if __name__ == '__main__':
    print("Initializing database...")
    init_db()
    print("Starting Flask server...")
    app.run(debug=False, host="0.0.0.0")