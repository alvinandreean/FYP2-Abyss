import tensorflow as tf
import os
from PIL import Image
import numpy as np
import time
import io
import base64

class FGSM:
    def __init__(self, epsilon=0.05, model_name='mobilenet_v2'):
        self.epsilon = epsilon
        self.model_name = model_name.lower()
        self.model = None
        self.image_size = (0, 0)
        print("Loading pretrained model...")
        
        self.load_model()
        self.model.trainable = False
        
    def np_to_base64(self, img_array: np.ndarray):
        """
        Convert a float32 [0..1] image array to a PNG Base64 string.
        """
        # Ensure array is in [0, 255] range
        img_array_255 = np.clip(img_array * 255, 0, 255).astype(np.uint8)
        pil_img = Image.fromarray(img_array_255)
        buffer = io.BytesIO()
        pil_img.save(buffer, format='PNG')
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
        
    def load_model(self):
        if self.model_name == 'mobilenet_v2':  # Load MobileNetV2
            self.model = tf.keras.applications.MobileNetV2(include_top=True, weights='imagenet')
            self.decode_predictions = tf.keras.applications.mobilenet_v2.decode_predictions
            self.preprocess_input = tf.keras.applications.mobilenet_v2.preprocess_input
            self.image_size = (224, 224)
        elif self.model_name == 'inception_v3':
            self.model = tf.keras.applications.InceptionV3(include_top=True, weights='imagenet')
            self.decode_predictions = tf.keras.applications.inception_v3.decode_predictions
            self.preprocess_input = tf.keras.applications.inception_v3.preprocess_input
            self.image_size = (299, 299)
        elif self.model_name == 'vgg19':  # Load VGG19
            self.model = tf.keras.applications.VGG19(include_top=True, weights='imagenet')
            self.decode_predictions = tf.keras.applications.vgg19.decode_predictions
            self.preprocess_input = tf.keras.applications.vgg19.preprocess_input
            self.image_size = (224, 224)
        elif self.model_name == 'densenet121':  # Load DenseNet121
            self.model = tf.keras.applications.DenseNet121(include_top=True, weights='imagenet')
            self.decode_predictions = tf.keras.applications.densenet.decode_predictions
            self.preprocess_input = tf.keras.applications.densenet.preprocess_input
            self.image_size = (224, 224)
        else:
            raise ValueError("Unsupported model.")

    def preprocess(self, image_input):
        if isinstance(image_input, tf.Tensor):
            try:
                image = tf.image.decode_image(image_input, channels=3)
                image.set_shape([None, None, 3])
            except:
                image = image_input
            image_np = image.numpy() if hasattr(image, 'numpy') else np.array(image)
            pil_image = Image.fromarray(np.uint8(image_np))
        elif isinstance(image_input, str):
            pil_image = Image.open(image_input)
        else:
            raise TypeError("Image input must be a file path or a tensor")
        
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        pil_image = pil_image.resize(self.image_size, Image.Resampling.LANCZOS)
        image_array = np.array(pil_image)
        image = tf.convert_to_tensor(image_array)
        image = tf.cast(image, tf.float32)
        image = self.preprocess_input(image)
        image = image[None, ...]  # Add batch dimension
        return image

    def get_imagenet_label(self, probs):
        try:
            result = self.decode_predictions(probs, top=1)[0][0]
            _, class_name, confidence = result
            class_name = class_name.encode('ascii', 'replace').decode('ascii')
            return result[0], class_name, confidence
        except Exception as e:
            print(f"Error in get_imagenet_label: {e}")
            return ("unknown", "unknown", 0.0)

    def create_adversarial_pattern(self, input_image, input_label):
        loss_object = tf.keras.losses.CategoricalCrossentropy()
        with tf.GradientTape() as tape:
            tape.watch(input_image)
            prediction = self.model(input_image)
            loss = loss_object(input_label, prediction)
        gradient = tape.gradient(loss, input_image)
        return tf.sign(gradient)

    def attack(self, image_path):
        start_time = time.time()
        try:
            image = self.preprocess(image_path)
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None

        # Original prediction
        image_probs = self.model.predict(image, verbose=0)
        _, orig_class, orig_conf = self.get_imagenet_label(image_probs)

        # Prepare one-hot target
        predicted_class_idx = tf.argmax(image_probs[0]).numpy()
        target = tf.one_hot(predicted_class_idx, image_probs.shape[-1])
        target = tf.reshape(target, (1, image_probs.shape[-1]))

        # Create adversarial image
        perturbations = self.create_adversarial_pattern(image, target)
        adversarial_image = image + self.epsilon * perturbations

        if self.model_name in ['mobilenet_v2', 'inception_v3', 'vgg19', 'densenet121']:
            adversarial_image = tf.clip_by_value(adversarial_image, -1, 1)
        else:
            raise NotImplementedError("Model not supported for clipping.")

        # Adversarial prediction
        adv_probs = self.model.predict(adversarial_image, verbose=0)
        _, adv_class, adv_conf = self.get_imagenet_label(adv_probs)

        # Return separate images + info
        results = self.display_attack_results(
            image, perturbations, adversarial_image,
            orig_class, adv_class, orig_conf, adv_conf
        )
        end_time = time.time()
        print(f"Attack completed in {end_time - start_time:.2f} seconds")
        print("Model Name:", self.model_name)
        # We can also attach epsilon or other info
        results["epsilon_used"] = self.epsilon
        return results

    def auto_tune_attack(self, image_path, epsilon_min=0.0001, epsilon_max=1, coarse_step=0.05, fine_step=0.001, min_confidence=0.01):
        start_time = time.time()

        print(self.model_name.upper())
        try:
            image = self.preprocess(image_path)
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None, None, None, None

        image_probs = self.model.predict(image, verbose=0)
        _, orig_class, orig_conf = self.get_imagenet_label(image_probs)
        print(f"Original Prediction: {orig_class} ({orig_conf * 100:.2f}%)")

        predicted_class_idx = tf.argmax(image_probs[0]).numpy()
        target = tf.one_hot(predicted_class_idx, image_probs.shape[-1])
        target = tf.reshape(target, (1, image_probs.shape[-1]))

        perturbations = self.create_adversarial_pattern(image, target)

        best_epsilon = None
        best_adv_image = None
        best_adv_class = None
        best_adv_conf = None

        # Step 1: Coarse search (larger step to quickly find a good epsilon range)
        epsilon = epsilon_min
        while epsilon <= epsilon_max:
            adv_image = tf.clip_by_value(image + epsilon * perturbations, -1, 1)
            adv_probs = self.model.predict(adv_image, verbose=0)
            _, adv_class, adv_conf = self.get_imagenet_label(adv_probs)

            print(f"Coarse Search: Trying ε = {epsilon:.5f} -> Class: {adv_class}, Confidence: {adv_conf*100:.2f}%")

            # If we find a misclassification with sufficient confidence, stop
            if adv_class != orig_class and adv_conf >= min_confidence:
                print(f"  ✓ Coarse Search: Attack succeeded with sufficient confidence!")
                best_epsilon = epsilon
                best_adv_image = adv_image
                best_adv_class = adv_class
                best_adv_conf = adv_conf
                break

            epsilon += coarse_step

        # Step 2: Fine search (narrow down epsilon with small steps)
        if best_epsilon is not None:
            # Fine search (narrowing down epsilon in small steps)
            epsilon_start = max(epsilon_min, best_epsilon - coarse_step)  # Start from the last candidate
            epsilon_end = min(epsilon_max, best_epsilon + coarse_step)    # Limit the epsilon range
            epsilon = epsilon_start

            while epsilon <= epsilon_end:
                adv_image = tf.clip_by_value(image + epsilon * perturbations, -1, 1)
                adv_probs = self.model.predict(adv_image, verbose=0)
                _, adv_class, adv_conf = self.get_imagenet_label(adv_probs)

                print(f"Fine Search: Trying ε = {epsilon:.6f} -> Class: {adv_class}, Confidence: {adv_conf*100:.2f}%")

                if adv_class != orig_class and adv_conf >= min_confidence:
                    best_epsilon = epsilon
                    best_adv_image = adv_image
                    best_adv_class = adv_class
                    best_adv_conf = adv_conf
                    break

                epsilon += fine_step

        end_time = time.time()
        duration = end_time - start_time

        if best_epsilon is not None:
            print(f"\n✅ Attack successful! Minimum ε ≈ {best_epsilon:.6f}")
            print(f"Adversarial Class: {best_adv_class} | Confidence: {best_adv_conf * 100:.2f}%")
            print(f"⏱️ Auto-tune completed in {duration:.2f} seconds")

            results = self.display_attack_results(
                image, perturbations, best_adv_image,
                orig_class, best_adv_class, orig_conf, best_adv_conf
            )
            results["epsilon_used"] = best_epsilon
            return results
        else:
            print(f"\n❌ Attack failed. No epsilon in range caused misclassification with {min_confidence*100:.0f}% confidence.")
            print(f"⏱️ Auto-tune completed in {duration:.2f} seconds")
            return None

    def display_attack_results(self, original_image, perturbation, adversarial_image, 
                               orig_class, adv_class, orig_conf, adv_conf):
        """
        Return separate Base64 images for original, perturbation, and adversarial images.
        """
        # Convert [-1..1] range -> [0..1] for display
        display_original = np.clip(original_image[0] * 0.5 + 0.5, 0, 1)
        display_adv = np.clip(adversarial_image[0] * 0.5 + 0.5, 0, 1)
        display_pert = np.clip(perturbation[0] * 0.5 + 0.5, 0, 1)

        # Convert each to Base64
        b64_original = self.np_to_base64(display_original)
        b64_pert = self.np_to_base64(display_pert)
        b64_adv = self.np_to_base64(display_adv)

        return {
            "original_image": b64_original,
            "perturbation_image": b64_pert,
            "adversarial_image": b64_adv,
            "orig_class": orig_class,
            "adv_class": adv_class,
            "orig_conf": float(orig_conf),
            "adv_conf": float(adv_conf),
        }

def main():
    # image_path = "image/animals/val/dog/dog1.jpg"  # Change image path here
    image_path = "image/ferrari.jpeg"  # Change image path here
    
    # Test with multiple models
    models = ['mobilenet_v2', 'inception_v3'] # 'vgg19', 'densenet121', resnet50 WIP
    
    for model_name in models:
        print(f"\n{'='*50}\nTesting with {model_name.upper()}\n{'='*50}")
        # Create FGSM attack instance for current model
        fgsm = FGSM(epsilon=0.05, model_name=model_name)
        
        # Run auto-tuning attack
        fgsm.auto_tune_attack(image_path)

if __name__ == "__main__":
    main()


