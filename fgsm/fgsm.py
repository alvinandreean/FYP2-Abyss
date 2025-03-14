import tensorflow as tf
import matplotlib
import matplotlib.pyplot as plt
import sys
import io
import os
import argparse

# Fix encoding issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

matplotlib.rcParams['figure.figsize'] = (8, 8)
matplotlib.rcParams['axes.grid'] = False

def main(image_path=None):
    # Parse command line arguments if no image path is provided
    if image_path is None:
        parser = argparse.ArgumentParser(description='Run FGSM attack on an image')
        parser.add_argument('--image', type=str, help='Path to the input image')
        args = parser.parse_args()
        
        if args.image:
            image_path = args.image
        else:
            print("No image path provided. Please provide an image path using --image argument")
            print("Using default image from ImageNet as fallback...")
            image_path = tf.keras.utils.get_file('YellowLabradorLooking_new.jpg', 
                                               'https://storage.googleapis.com/download.tensorflow.org/example_images/YellowLabradorLooking_new.jpg')

    # Load pretrained model
    print("Loading pretrained model...")
    pretrained_model = tf.keras.applications.MobileNetV2(include_top=True,
                                                        weights='imagenet')
    pretrained_model.trainable = False

    # ImageNet labels
    decode_predictions = tf.keras.applications.mobilenet_v2.decode_predictions

    # Helper function to preprocess the image so that it can be inputted in MobileNetV2
    def preprocess(image):
        image = tf.cast(image, tf.float32)
        image = tf.image.resize(image, (224, 224))
        image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
        image = image[None, ...]
        return image

    # Helper function to extract labels from probability vector
    def get_imagenet_label(probs):
        try:
            # Handle potential Unicode issues in label names
            result = decode_predictions(probs, top=1)[0][0]
            # Replace any problematic characters in the class name
            _, class_name, confidence = result
            class_name = class_name.encode('ascii', 'replace').decode('ascii')
            return (result[0], class_name, confidence)
        except Exception as e:
            print(f"Error in get_imagenet_label: {e}")
            return ("unknown", "unknown", 0.0)

    # Load and preprocess the image
    print(f"Loading and preprocessing image from: {image_path}")
    try:
        # Check if the image path is a local file
        if os.path.isfile(image_path):
            image_raw = tf.io.read_file(image_path)
        else:
            # If not a local file, try to download it
            print("Image not found locally, attempting to download...")
            image_raw = tf.io.read_file(image_path)
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    # Try different decoders based on file extension
    try:
        file_ext = os.path.splitext(image_path)[1].lower()
        if file_ext == '.png':
            image = tf.image.decode_png(image_raw, channels=3)
        elif file_ext in ['.jpg', '.jpeg']:
            image = tf.image.decode_jpeg(image_raw, channels=3)
        else:
            # Try generic decoder
            image = tf.image.decode_image(image_raw, channels=3)
            # Set shape information since decode_image doesn't set it
            image.set_shape([None, None, 3])
    except Exception as e:
        print(f"Error decoding image: {e}")
        print("Trying generic image decoder...")
        try:
            image = tf.image.decode_image(image_raw, channels=3)
            image.set_shape([None, None, 3])
        except Exception as e2:
            print(f"Failed to decode image: {e2}")
            return

    # Create output directory for results
    output_dir = "fgsm_results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Preprocess the image
    image = preprocess(image)
    
    print("Running prediction on original image...")
    image_probs = pretrained_model.predict(image, verbose=0)

    # Display original image
    plt.figure()
    plt.imshow(image[0] * 0.5 + 0.5)  # To change [-1, 1] to [0,1]
    _, image_class, class_confidence = get_imagenet_label(image_probs)
    plt.title(f'{image_class} : {class_confidence*100:.2f}% Confidence')
    plt.savefig(os.path.join(output_dir, 'original_image.png'))
    plt.close()
    print(f"Original image classified as: {image_class} with {class_confidence*100:.2f}% confidence")

    # Define loss function for creating adversarial examples
    loss_object = tf.keras.losses.CategoricalCrossentropy()

    def create_adversarial_pattern(input_image, input_label):
        with tf.GradientTape() as tape:
            tape.watch(input_image)
            prediction = pretrained_model(input_image)
            loss = loss_object(input_label, prediction)

        # Get the gradients of the loss w.r.t to the input image.
        gradient = tape.gradient(loss, input_image)
        # Get the sign of the gradients to create the perturbation
        signed_grad = tf.sign(gradient)
        return signed_grad

    # Get the input label of the image (use the predicted class)
    print("Creating adversarial pattern...")
    predicted_class_idx = tf.argmax(image_probs[0]).numpy()
    print(f"Using predicted class index: {predicted_class_idx}")
    label = tf.one_hot(predicted_class_idx, image_probs.shape[-1])
    label = tf.reshape(label, (1, image_probs.shape[-1]))

    # Create perturbations
    perturbations = create_adversarial_pattern(image, label)
    
    # Display perturbation pattern
    plt.figure()
    plt.imshow(perturbations[0] * 0.5 + 0.5)  # To change [-1, 1] to [0,1]
    plt.title('Perturbation Pattern')
    plt.savefig(os.path.join(output_dir, 'perturbation_pattern.png'))
    plt.close()
    print(f"Perturbation pattern saved to {output_dir}/perturbation_pattern.png")

    def display_images(image, description, filename):
        try:
            prediction = pretrained_model.predict(image, verbose=0)
            _, label, confidence = get_imagenet_label(prediction)
            plt.figure()
            plt.imshow(image[0]*0.5+0.5)
            plt.title(f'{description}\n{label}: {confidence*100:.2f}% Confidence')
            plt.savefig(os.path.join(output_dir, filename))
            plt.close()  # Close the figure to free memory
            print(f"{description}: classified as {label} with {confidence*100:.2f}% confidence")
        except Exception as e:
            print(f"Error displaying image {description}: {e}")

    # Test with different epsilon values
    print("Generating adversarial examples with different epsilon values...")
    epsilons = [0, 0.01, 0.1, 0.15]
    descriptions = [('Epsilon = {:.3f}'.format(eps) if eps else 'Input')
                    for eps in epsilons]
    
    for i, eps in enumerate(epsilons):
        adv_x = image + eps*perturbations
        adv_x = tf.clip_by_value(adv_x, -1, 1)
        filename = f'adversarial_example_eps_{eps}.png'
        display_images(adv_x, descriptions[i], filename)

    print(f"All adversarial examples have been generated and saved to {output_dir}/")

if __name__ == "__main__":
    try:
        main("image\panda.jpg")
    except Exception as e:
        print(f"An error occurred: {e}")





