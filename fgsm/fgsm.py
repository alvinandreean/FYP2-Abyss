import tensorflow as tf
import matplotlib
import matplotlib.pyplot as plt
import os
from PIL import Image
import numpy as np

class FGSM:
    def __init__(self, epsilon=0.05):
        """
        Initialize FGSM attack.
        Args:
            epsilon: perturbation magnitude
        """
        self.epsilon = epsilon
        print("Loading pretrained model...")
        self.model = tf.keras.applications.MobileNetV2(include_top=True, weights='imagenet')
        self.model.trainable = False
        self.decode_predictions = tf.keras.applications.mobilenet_v2.decode_predictions

    def preprocess(self, image_input):
        """
        Preprocess the image using Pillow and convert for MobileNetV2.
        
        Args:
            image_input: Can be a file path string or a tensor from tf.io.read_file
        """
        # Check if input is already a tensor
        if isinstance(image_input, tf.Tensor):
            # If it's a tensor, we need to decode it first
            try:
                # If it's raw image data from read_file
                image = tf.image.decode_image(image_input, channels=3)
                image.set_shape([None, None, 3])
            except:
                # If it's already an image tensor
                image = image_input
                
            # Using PIL to process the image
            image_np = image.numpy() if hasattr(image, 'numpy') else np.array(image)
            pil_image = Image.fromarray(np.uint8(image_np))
        
        elif isinstance(image_input, str):
            # If input is a file path
            pil_image = Image.open(image_input)
        
        else:
            raise TypeError("Image input must be a file path or a tensor")
        
        # Convert to RGB if it's not already
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Resize using PIL's high-quality resampling
        pil_image = pil_image.resize((224, 224), Image.Resampling.LANCZOS)
        
        # Convert to numpy array
        image_array = np.array(pil_image)
        
        # Convert to TensorFlow tensor and apply MobileNetV2 preprocessing
        image = tf.convert_to_tensor(image_array)
        image = tf.cast(image, tf.float32)
        image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
        
        # Add batch dimension
        image = image[None, ...]
        
        return image

    def get_imagenet_label(self, probs):
        """Extract the label and confidence from the model's probability vector."""
        try:
            result = self.decode_predictions(probs, top=1)[0][0]
            _, class_name, confidence = result
            class_name = class_name.encode('ascii', 'replace').decode('ascii')
            return result[0], class_name, confidence
        except Exception as e:
            print(f"Error in get_imagenet_label: {e}")
            return ("unknown", "unknown", 0.0)

    def create_adversarial_pattern(self, input_image, input_label):
        """Generate untargeted adversarial perturbation using FGSM."""
        loss_object = tf.keras.losses.CategoricalCrossentropy()
        
        with tf.GradientTape() as tape:
            tape.watch(input_image)
            prediction = self.model(input_image)
            loss = loss_object(input_label, prediction)
        
        gradient = tape.gradient(loss, input_image)
        return tf.sign(gradient)

    def attack(self, image_path):
        """
        Perform FGSM attack on the given image.
        Args:
            image_path: path to input image
        """
        # Output directory
        output_dir = "fgsm_results"
        os.makedirs(output_dir, exist_ok=True)

        try:
            image = self.preprocess(image_path)
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return

        # Get the original prediction from the model
        image_probs = self.model.predict(image, verbose=0)
        _, orig_class, orig_conf = self.get_imagenet_label(image_probs)

        # Create the target adversarial example
        predicted_class_idx = tf.argmax(image_probs[0]).numpy()
        target = tf.one_hot(predicted_class_idx, image_probs.shape[-1])
        target = tf.reshape(target, (1, image_probs.shape[-1]))

        # Generate the perturbation 
        perturbations = self.create_adversarial_pattern(image, target)
        
        # Apply the perturbation to the image
        adversarial_image = image + self.epsilon * perturbations
        adversarial_image = tf.clip_by_value(adversarial_image, -1, 1)
        
        # Get adversarial prediction from the model
        adv_probs = self.model.predict(adversarial_image, verbose=0)
        _, adv_class, adv_conf = self.get_imagenet_label(adv_probs)

        # Display the attack results
        self.display_attack_results(
            image, perturbations, adversarial_image,
            orig_class, adv_class, orig_conf, adv_conf,
            output_dir
        )

    def auto_tune_attack(self, image_path, epsilon_start=0.001, epsilon_end=0.1, step=0.001):
        """
        Automatically tune epsilon to find the smallest value that causes misclassification.
        """
        output_dir = "fgsm_results"
        os.makedirs(output_dir, exist_ok=True)

        try:
            image = self.preprocess(image_path)
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return

        # Get the original prediction
        image_probs = self.model.predict(image, verbose=0)
        _, orig_class, orig_conf = self.get_imagenet_label(image_probs)
        print(f"Original Prediction: {orig_class} ({orig_conf * 100:.2f}%)")

        # Prepare target one-hot label
        predicted_class_idx = tf.argmax(image_probs[0]).numpy()
        target = tf.one_hot(predicted_class_idx, image_probs.shape[-1])
        target = tf.reshape(target, (1, image_probs.shape[-1]))

        # Start auto-tuning loop
        epsilon = epsilon_start
        success = False
        best_result = None

        while epsilon <= epsilon_end:
            perturbations = self.create_adversarial_pattern(image, target)
            adversarial_image = image + epsilon * perturbations
            adversarial_image = tf.clip_by_value(adversarial_image, -1, 1)

            # Predict adversarial image
            adv_probs = self.model.predict(adversarial_image, verbose=0)
            _, adv_class, adv_conf = self.get_imagenet_label(adv_probs)

            print(f"ε={epsilon:.4f} | Adversarial Prediction: {adv_class} ({adv_conf * 100:.2f}%)")

            if adv_class != orig_class:
                success = True
                best_result = (epsilon, adv_class, adv_conf)
                # Optional: break on first success
                break

            epsilon += step

        if success:
            print(f"\n✅ Attack successful! Minimum ε = {best_result[0]:.4f}")
            print(f"Adversarial Class: {best_result[1]} | Confidence: {best_result[2] * 100:.2f}%")
            # Optional: Visualize this successful attack
            self.display_attack_results(
                image, perturbations, adversarial_image,
                orig_class, best_result[1], orig_conf, best_result[2],
                output_dir
            )
        else:
            print("\n❌ Attack failed. No epsilon in range caused misclassification.")


    def display_attack_results(self, original_image, perturbation, adversarial_image, 
                             orig_class, adv_class, orig_conf, adv_conf, output_dir):
        """Display and save attack results in a single, detailed figure."""

        plt.figure(figsize=(20, 7))
        
        # Original image
        plt.subplot(1, 3, 1)
        plt.imshow(original_image[0] * 0.5 + 0.5)
        plt.title('Original Image', fontsize=14, pad=10)
        plt.axis('off')
        plt.text(0.5, -0.15, f'Class: {orig_class}\nConfidence: {orig_conf*100:.2f}%', 
                ha='center', va='center', transform=plt.gca().transAxes, 
                fontsize=12, color='black')
        
        # Perturbation
        plt.subplot(1, 3, 2)
        plt.imshow(perturbation[0] * 0.5 + 0.5)
        plt.title('Perturbation', fontsize=14, pad=10)
        plt.axis('off')
        plt.text(0.5, -0.15, f'ε = {self.epsilon}', 
                ha='center', va='center', transform=plt.gca().transAxes, 
                fontsize=12, color='black')
        
        # Adversarial image
        plt.subplot(1, 3, 3)
        plt.imshow(adversarial_image[0] * 0.5 + 0.5)
        plt.title('Adversarial Image', fontsize=14, pad=10)
        plt.axis('off')
        plt.text(0.5, -0.15, f'Class: {adv_class}\nConfidence: {adv_conf*100:.2f}%', 
                ha='center', va='center', transform=plt.gca().transAxes, 
                fontsize=12, color='black')
        
        # Title
        plt.suptitle('FGSM Attack Results', fontsize=16, y=1)
        
        # Adjust layout and save
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'fgsm_attack_results.png'), 
                    bbox_inches='tight', dpi=300)
        plt.close()

def main():
        # Path to the image you want to test
        image_path = "image/panda.jpg"  # Change this to your image path

        # Create FGSM instance (epsilon is irrelevant here because auto-tune calculates it)
        fgsm = FGSM()

        # Run the auto-tuning attack
        fgsm.auto_tune_attack(
            
            image_path=image_path,
            epsilon_start=0.001,   # Start testing from 0.001
            epsilon_end=0.1,       # Stop testing at 0.1 if not successful
            step=0.001             # Increase epsilon by 0.001 each loop
        )

if __name__ == "__main__":
    main()


# def main():
#     # image_path = "image/animals/val/dog/dog1.jpg"  # Change image path here
#     image_path = "image/panda.jpg"
    
#     # Create FGSM attack instance, can adjust epsilon here
#     fgsm = FGSM(epsilon=0.05)
    
#     fgsm.attack(image_path)

# if __name__ == "__main__":
#     main()
    
    
    