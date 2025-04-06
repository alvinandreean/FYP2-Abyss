from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from fgsm import FGSM  # import your modified FGSM class

app = Flask(__name__)
CORS(app)

# Create a global FGSM instance with default settings
fgsm = FGSM(epsilon=0.05, model_name='mobilenet_v2')

@app.route('/attack', methods=['POST'])
def attack():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    epsilon_str = request.form.get('epsilon', '0.05')
    auto_tune_str = request.form.get('autoTune', 'false')
    epsilon_value = float(epsilon_str)
    auto_tune = auto_tune_str.lower() == 'true'

    image_file = request.files['image']
    filepath = "temp_image.jpg"  # Temporary storage if needed
    image_file.save(filepath)

    try:
        if auto_tune:
            results = fgsm.auto_tune_attack(filepath)
        else:
            fgsm.epsilon = epsilon_value
            results = fgsm.attack(filepath)

        if not results:
            return jsonify({'error': 'Attack failed'}), 500

        # Return the entire results dictionary
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
