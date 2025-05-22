from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from fgsm import FGSM  # your FGSM class
from auth import register_user, login_user, verify_token
from flask_bcrypt import Bcrypt
from db import execute_query, get_connection
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Configure CORS to allow requests from any origin
CORS(app, resources={r"/*": {"origins": "*"}})
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

    try:
        # Save uploaded image to temp file with a unique name
        image_file = request.files['image']
        import uuid
        import datetime
        
        # File type validation (allow only image extensions)
        allowed_extensions = {'jpg', 'jpeg', 'png', 'bmp', 'gif'}
        filename = secure_filename(image_file.filename)
        if '.' not in filename or filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify({'error': 'Invalid file type. Only image files (jpg, jpeg, png, bmp, gif) are allowed.'}), 400

        # Create unique filename to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"temp_image_{timestamp}_{unique_id}.jpg"
        
        image_path = safe_filename
        print(f"Saving uploaded image to {image_path}")
        image_file.save(image_path)

        # Attack
        print(f"Running {'auto-tune' if auto_tune else 'regular'} attack with model {model_name}")
        if auto_tune:
            results = fgsm.auto_tune_attack(image_path)
            print(f"Auto-tune attack completed, results: {'Success' if results else 'Failed'}")
        else:
            fgsm.epsilon = epsilon_value
            results = fgsm.attack(image_path)
            print(f"Regular attack completed, results: {'Success' if results else 'Failed'}")

        # Clean up temp file 
        try:
            os.remove(image_path)
            print(f"Cleaned up temporary file {image_path}")
        except Exception as e:
            print(f"Warning: Failed to remove temp file {image_path}: {e}")

        if results:
            # Optionally attach the model name used, so it can be displayed
            results["model_used"] = model_name
            return jsonify(results)
        else:
            # If results is None, the attack failed
            error_msg = "Attack failed. The model might not be able to classify the image or find an adversarial example."
            print(error_msg)
            return jsonify({'error': error_msg}), 500
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in attack: {str(e)}")
        print(f"Detailed traceback: {error_details}")
        return jsonify({'error': f'Attack error: {str(e)}'}), 500

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
        import uuid
        import datetime
        
        print(f"Downloading image from URL: {image_url}")
        response = requests.get(image_url)
        
        # Create unique filename to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"temp_image_{timestamp}_{unique_id}.jpg"
        
        # Opening and saving as JPEG for compatibility
        try:
            image = Image.open(BytesIO(response.content))
            # Handle RGBA images by creating a white background
            if image.mode == 'RGBA':
                print(f"Converting RGBA image to RGB with white background")
                # Create a white background image
                background = Image.new('RGB', image.size, (255, 255, 255))
                # Paste the image on the background using alpha channel as mask
                background.paste(image, mask=image.split()[3])
                image = background
            elif image.mode != 'RGB':
                print(f"Converting image from {image.mode} to RGB")
                image = image.convert('RGB')
            image_path = safe_filename
            print(f"Saving image to {image_path}")
            image.save(image_path, format='JPEG', quality=95)
        except Exception as image_error:
            print(f"Error processing downloaded image: {str(image_error)}")
            return jsonify({'error': f'Error processing image: {str(image_error)}'}), 500
        
        # Attack
        print(f"Running {'auto-tune' if auto_tune else 'regular'} attack with model {model_name}")
        if auto_tune:
            results = fgsm.auto_tune_attack(image_path)
            print(f"Auto-tune attack completed, results: {'Success' if results else 'Failed'}")
        else:
            fgsm.epsilon = epsilon_value
            results = fgsm.attack(image_path)
            print(f"Regular attack completed, results: {'Success' if results else 'Failed'}")

        # Clean up temp file 
        try:
            os.remove(image_path)
            print(f"Cleaned up temporary file {image_path}")
        except Exception as e:
            print(f"Warning: Failed to remove temp file {image_path}: {e}")

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
                    try:
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
                    except Exception as e:
                        print(f"Error saving to history: {str(e)}")
                        # Continue even if history saving fails
            
            return jsonify(results)
        else:
            # If results is None, the attack failed
            error_msg = "Attack failed. The model might not be able to classify the image or find an adversarial example."
            print(error_msg)
            return jsonify({'error': error_msg}), 500
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in attack_from_url: {str(e)}")
        print(f"Detailed traceback: {error_details}")
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

@app.route('/model-info', methods=['GET'])
def get_model_info():
    try:
        # Information based on TensorFlow documentation
        models_info = [
            {
                "model_name": "MobileNet V2",
                "architecture": "Convolutional Neural Network (CNN)",
                "accuracy": 0.901,  # 90.1%
                "misclassification_success_rate": 0.78,  # 78%
                "parameters": 3538984,  # ~3.5 million parameters
                "training_dataset": "ImageNet",
                "description": "MobileNetV2 is a lightweight CNN architecture designed for mobile and edge devices. It uses inverted residuals and linear bottlenecks to achieve high accuracy while maintaining computational efficiency. The model is particularly suited for applications with limited computational resources."
            },
            {
                "model_name": "Inception V3",
                "architecture": "Inception Network",
                "accuracy": 0.937,  # 93.7%
                "misclassification_success_rate": 0.72,  # 72%
                "parameters": 23851784,  # ~23.8 million parameters
                "training_dataset": "ImageNet",
                "description": "Inception V3 is a deep CNN architecture that builds on previous Inception models by incorporating additional factorization methods. It uses asymmetric convolutions, auxiliary classifiers, and batch normalization to achieve high accuracy. The model was designed to be computationally efficient while maintaining high performance on image classification tasks."
            }
        ]
        
        print("Successfully prepared model info data")
        response = jsonify(models_info)
        return response, 200
    except Exception as e:
        print(f"Error fetching model information: {str(e)}")
        return jsonify({'error': f'Failed to retrieve model information: {str(e)}'}), 500

if __name__ == '__main__':
    print("Initializing database...")
    init_db()
    print("Starting Flask server...")
    app.run(debug=False, host="0.0.0.0")