from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from fgsm import FGSM  # import your modified FGSM class

app = Flask(__name__)
CORS(app)

@app.route('/attack', methods=['POST'])
def attack():
    if 'image' not in request.files or 'model' not in request.form:
        return jsonify({'error': 'No image or model provided'}), 400

    model_name = request.form['model']  # Get the model name from the request
    epsilon_value = float(request.form.get('epsilon', 0.05))
    auto_tune = request.form.get('autoTune', 'false').lower() == 'true'

    # Initialize the FGSM class with the selected model
    fgsm = FGSM(epsilon=epsilon_value, model_name=model_name)

    # Process the image and run the attack
    image_file = request.files['image']
    image_path = "temp_image.jpg"
    image_file.save(image_path)

    # Choose attack method based on autoTune flag
    if auto_tune:
        results = fgsm.auto_tune_attack(image_path)
    else:
        fgsm.epsilon = epsilon_value
        results = fgsm.attack(image_path)

    if results:
        return jsonify(results)
    else:
        return jsonify({'error': 'Attack failed'}), 500


if __name__ == '__main__':
    app.run(debug=True)
