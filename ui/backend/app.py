from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import io
from PIL import Image
import numpy as np
from fgsm import FGSM  # import your FGSM class

app = Flask(__name__)
CORS(app)  # enable CORS so React can call the API

# Initialize FGSM with default settings (adjust epsilon or model as needed)
fgsm = FGSM(epsilon=0.05, model_name='mobilenet_v2')

@app.route('/attack', methods=['POST'])
def attack():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image_file = request.files['image']
    
    # Save the image temporarily or process it in-memory
    try:
        # Option 1: Save the image temporarily
        filepath = "temp_image.jpg"
        image_file.save(filepath)
        
        # Run the auto-tune FGSM attack
        best_epsilon = fgsm.auto_tune_attack(filepath)
        
        # Load the adversarial result image from file (or modify FGSM to return image arrays)
        result_path = "fgsm_results/mobilenet_v2/fgsm_attack_results.png"
        with open(result_path, "rb") as img_file:
            b64_image = base64.b64encode(img_file.read()).decode('utf-8')
        
        response = {
            "epsilon": best_epsilon,
            "original_class": "/* add original class info */",
            "adversarial_class": "/* add adversarial class info */",
            "result_image": b64_image
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
