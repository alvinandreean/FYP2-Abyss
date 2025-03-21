import tensorflow as tf
import matplotlib
import matplotlib.pyplot as plt
import os
from PIL import Image
import numpy as np
import time

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
        start_time = time.time()
        
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
        
        end_time = time.time()
        print(f"Attack completed in {end_time - start_time:.2f} seconds")

    def auto_tune_attack(self, image_path, epsilon_min=0.001, epsilon_max=1, precision=0.0001, max_iterations=30):
        """
        Auto-tune the epsilon parameter to find the minimum value that causes misclassification.
        Uses binary search for efficiency.
        """
        # Start timer
        start_time = time.time()
        
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

        # Precompute perturbations
        perturbations = self.create_adversarial_pattern(image, target)
        
        # First, verify if attack is possible within the range
        max_adv_image = tf.clip_by_value(image + epsilon_max * perturbations, -1, 1)
        max_probs = self.model.predict(max_adv_image, verbose=0)
        _, max_class, max_conf = self.get_imagenet_label(max_probs)
        
        if max_class == orig_class:
            print(f"❌ Even maximum ε={epsilon_max} doesn't change classification.")
            print(f"Try increasing the maximum epsilon value.")
            end_time = time.time()
            print(f"⏱️ Auto-tune completed in {end_time - start_time:.2f} seconds")
            return None
        
        # Initialize binary search
        left, right = epsilon_min, epsilon_max
        best_epsilon = None
        best_adv_image = None
        best_adv_class = None
        best_adv_conf = None
        
        iterations = 0
        
        print(f"Starting binary search with ε range [{epsilon_min}, {epsilon_max}]")
        
        # binary search
        while (right - left) > precision and iterations < max_iterations:
            iterations += 1
            mid = (left + right) / 2
            print(f"Iteration {iterations}: Trying ε = {mid:.6f}")
            
            # Create adversarial image with current epsilon
            adv_image = tf.clip_by_value(image + mid * perturbations, -1, 1)
            
            # Check if attack succeeds
            adv_probs = self.model.predict(adv_image, verbose=0)
            _, adv_class, adv_conf = self.get_imagenet_label(adv_probs)
            
            print(f"  Class: {adv_class}, Confidence: {adv_conf*100:.2f}%")
            
            if adv_class != orig_class:
                # Attack succeeded, try smaller epsilon
                print(f"  ✓ Attack succeeded!")
                best_epsilon = mid
                best_adv_image = adv_image
                best_adv_class = adv_class
                best_adv_conf = adv_conf
                right = mid
            else:
                # Attack failed, try larger epsilon
                print(f"  ✗ Attack failed")
                left = mid
        
        # Final verification at the boundary
        if best_epsilon is not None:
            # Check if there's a smaller epsilon that works
            verify_eps = max(epsilon_min, best_epsilon - precision)
            verify_image = tf.clip_by_value(image + verify_eps * perturbations, -1, 1)
            verify_probs = self.model.predict(verify_image, verbose=0)
            _, verify_class, verify_conf = self.get_imagenet_label(verify_probs)
            
            if verify_class != orig_class:
                # Found even smaller epsilon
                print(f"Found even smaller working epsilon: {verify_eps:.6f}")
                best_epsilon = verify_eps
                best_adv_image = verify_image
                best_adv_class = verify_class
                best_adv_conf = verify_conf
        
        # End timer
        end_time = time.time()
        duration = end_time - start_time
        
        if best_epsilon is not None:
            print(f"\n✅ Attack successful! Minimum ε ≈ {best_epsilon:.6f}")
            print(f"Adversarial Class: {best_adv_class} | Confidence: {best_adv_conf * 100:.2f}%")
            print(f"⏱️ Auto-tune completed in {duration:.2f} seconds ({iterations} iterations)")
            
            # Update epsilon to use for display
            self.epsilon = best_epsilon
            
            # Display results with minimum successful epsilon
            self.display_attack_results(
                image, perturbations, best_adv_image,
                orig_class, best_adv_class, orig_conf, best_adv_conf,
                output_dir
            )
            return best_epsilon
        else:
            print(f"\n❌ Attack failed. No epsilon in range caused misclassification.")
            print(f"⏱️ Auto-tune completed in {duration:.2f} seconds ({iterations} iterations)")
            return None


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
    # image_path = "image/animals/val/dog/dog1.jpg"  # Change image path here
    image_path = "image/ferrari.jpeg"
    
    # Create FGSM attack instance, can adjust epsilon here
    fgsm = FGSM(epsilon=0.05)
    
    fgsm.auto_tune_attack(image_path)

if __name__ == "__main__":
    main()
    
    
    