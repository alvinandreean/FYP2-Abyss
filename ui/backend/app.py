from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import os
from fgsm import FGSM  # import your FGSM class

app = Flask(__name__)
CORS(app)

# Create a global FGSM instance with some default (will be overwritten anyway)
fgsm = FGSM(epsilon=0.05, model_name='mobilenet_v2')

@app.route('/attack', methods=['POST'])
def attack():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    # Get the posted form data
    epsilon_str = request.form.get('epsilon', '0.05')
    auto_tune_str = request.form.get('autoTune', 'false')
    
    epsilon_value = float(epsilon_str)
    auto_tune = auto_tune_str.lower() == 'true'

    # Save the image
    image_file = request.files['image']
    filepath = "temp_image.jpg"
    image_file.save(filepath)

    # Run either auto-tune or normal FGSM
    try:
        if auto_tune:
            best_epsilon = fgsm.auto_tune_attack(filepath)
            used_epsilon = best_epsilon
        else:
            fgsm.epsilon = epsilon_value
            fgsm.attack(filepath)
            used_epsilon = epsilon_value
        
        # The FGSM class in your code saves the final image as "fgsm_attack_results.png".
        # Adjust the path if needed, especially if you change output directory or model name.
        result_path = "fgsm_results/mobilenet_v2/fgsm_attack_results.png"
        
        # Convert the result image to base64
        if os.path.exists(result_path):
            with open(result_path, "rb") as img_file:
                b64_image = base64.b64encode(img_file.read()).decode('utf-8')
        else:
            return jsonify({'error': 'Result image not found'}), 500
        
        # TODO: If your FGSM class returns the actual classes and confidences, 
        # you can pass them here. For now, placeholders:
        response = {
            "epsilon": used_epsilon,
            "original_class": "OriginalClassPlaceholder",
            "adversarial_class": "AdversarialClassPlaceholder",
            "result_image": b64_image
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
