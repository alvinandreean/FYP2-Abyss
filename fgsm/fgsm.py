import tensorflow as tf
import matplotlib
import matplotlib.pyplot as plt
import sys
import io
import os
import argparse
import random

# Fix encoding issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

matplotlib.rcParams['figure.figsize'] = (8, 8)
matplotlib.rcParams['axes.grid'] = False

def preprocess(image):
    """Preprocess the image to be compatible with MobileNetV2."""
    image = tf.cast(image, tf.float32)
    image = tf.image.resize(image, (224, 224))
    image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
    return image[None, ...]

def get_imagenet_label(probs, decode_predictions):
    """Extract the label and confidence from the model's probability vector."""
    try:
        result = decode_predictions(probs, top=1)[0][0]
        _, class_name, confidence = result
        class_name = class_name.encode('ascii', 'replace').decode('ascii')
        return result[0], class_name, confidence
    except Exception as e:
        print(f"Error in get_imagenet_label: {e}")
        return ("unknown", "unknown", 0.0)

def create_adversarial_pattern(model, loss_object, input_image, input_label):
    """Generate untargeted adversarial perturbation using one-shot FGSM."""
    with tf.GradientTape() as tape:
        tape.watch(input_image)
        prediction = model(input_image)
        loss = loss_object(input_label, prediction)
    gradient = tape.gradient(loss, input_image)
    return tf.sign(gradient)

def create_targeted_adversarial_pattern(model, loss_object, input_image, target_label):
    """Generate targeted adversarial perturbation using one-shot FGSM (negative update)."""
    with tf.GradientTape() as tape:
        tape.watch(input_image)
        prediction = model(input_image)
        loss = loss_object(target_label, prediction)
    gradient = tape.gradient(loss, input_image)
    return tf.sign(gradient)

def iterative_fgsm_attack(model, loss_object, image, label, epsilon, num_steps, targeted=False):
    """
    Perform an iterative FGSM attack (I-FGSM).
    If targeted is True, subtract the update; otherwise, add it.
    """
    adv_image = tf.identity(image)
    step_size = epsilon / num_steps
    for i in range(num_steps):
        with tf.GradientTape() as tape:
            tape.watch(adv_image)
            prediction = model(adv_image)
            loss = loss_object(label, prediction)
        gradient = tape.gradient(loss, adv_image)
        if targeted:
            adv_image = adv_image - step_size * tf.sign(gradient)
        else:
            adv_image = adv_image + step_size * tf.sign(gradient)
        adv_image = tf.clip_by_value(adv_image, -1, 1)
    return adv_image

def display_image(model, image, description, filename, decode_predictions, output_dir):
    """
    Display and save the image with its predicted label and confidence.
    """
    prediction = model.predict(image, verbose=0)
    _, label_text, confidence = get_imagenet_label(prediction, decode_predictions)
    plt.figure()
    plt.imshow(image[0] * 0.5 + 0.5)  # Convert from [-1,1] to [0,1]
    plt.title(f'{description}\n{label_text}: {confidence * 100:.2f}% Confidence')
    plt.savefig(os.path.join(output_dir, filename))
    plt.close()
    print(f"{description}: classified as {label_text} with {confidence * 100:.2f}% confidence")

def main(image_path=None):
    parser = argparse.ArgumentParser(description='Run FGSM attack on an image')
    parser.add_argument('--image', type=str,
                        default="image/redpanda.png",
                        help='Path to the input image')
    parser.add_argument('--epsilon', type=float, default=0.05, help='Epsilon value for FGSM attack')
    parser.add_argument('--iterative', action='store_true', help='Use iterative FGSM (I-FGSM)')
    parser.add_argument('--num_steps', type=int, default=10, help='Number of steps for iterative attack')
    parser.add_argument('--targeted', action='store_true', help='Perform a targeted attack')
    parser.add_argument('--target_class', type=int, help='Target class index for a targeted attack (ImageNet index)')
    parser.add_argument('--reduce_confidence', action='store_true',
                        help='Reduce model confidence by maximizing output entropy')
    
    try:
        args = parser.parse_args()
    except Exception as e:
        # If parsing fails, try to get the image path directly
        import sys
        if len(sys.argv) > 1:
            image_path = sys.argv[1]
        args = parser.parse_args([])  # Parse with empty args
    
    # If image_path is provided as a parameter or through sys.argv, use it
    if image_path:
        args.image = image_path
    
    # Normalize the path
    image_path = os.path.normpath(args.image)
    
    if not os.path.isfile(image_path):
        # If the path doesn't exist, try to find it relative to the project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        alt_path = os.path.join(project_root, image_path)
        if os.path.isfile(alt_path):
            image_path = alt_path
    
    if not os.path.isfile(image_path):
        print(f"Error: Could not find image at {image_path}")
        return
    
    print(f"Using image: {image_path}")
    
    print("Loading pretrained model...")
    pretrained_model = tf.keras.applications.MobileNetV2(include_top=True, weights='imagenet')
    pretrained_model.trainable = False
    decode_predictions = tf.keras.applications.mobilenet_v2.decode_predictions

    print(f"Loading and preprocessing image from: {image_path}")
    try:
        image_raw = tf.io.read_file(image_path)
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    try:
        file_ext = os.path.splitext(image_path)[1].lower()
        if file_ext in ['.png', '.jpg', '.jpeg']:
            image = tf.image.decode_image(image_raw, channels=3)
            image.set_shape([None, None, 3])
        else:
            print("Unsupported file format.")
            return
    except Exception as e:
        print(f"Error decoding image: {e}")
        return

    output_dir = "fgsm_results"
    os.makedirs(output_dir, exist_ok=True)
    image = preprocess(image)

    print("Running prediction on original image...")
    image_probs = pretrained_model.predict(image, verbose=0)
    _, orig_class, class_confidence = get_imagenet_label(image_probs, decode_predictions)
    plt.figure()
    plt.imshow(image[0] * 0.5 + 0.5)
    plt.title(f'{orig_class} : {class_confidence * 100:.2f}% Confidence')
    plt.savefig(os.path.join(output_dir, 'original_image.png'))
    plt.close()
    print(f"Original image classified as: {orig_class} with {class_confidence * 100:.2f}% confidence")
    
    # Set up loss function
    if args.reduce_confidence:
        # Use KL divergence with a uniform target distribution to force low confidence.
        num_classes = image_probs.shape[-1]
        uniform_dist = tf.constant([1.0 / num_classes] * num_classes, shape=(1, num_classes))
        def kl_loss(dummy, prediction):
            # Compute KL divergence: sum(uniform * log(uniform / prediction))
            return tf.reduce_sum(uniform_dist * tf.math.log((uniform_dist + 1e-10) / (prediction + 1e-10)))
        loss_object = kl_loss
        label_to_use = None  # Not used in this loss.
        print("Using confidence reduction loss (KL divergence with uniform distribution) to lower model confidence.")
    else:
        loss_object = tf.keras.losses.CategoricalCrossentropy()
        # For untargeted attack, use the predicted label.
        predicted_class_idx = tf.argmax(image_probs[0]).numpy()
        true_label = tf.one_hot(predicted_class_idx, image_probs.shape[-1])
        true_label = tf.reshape(true_label, (1, image_probs.shape[-1]))
        label_to_use = true_label

    # For targeted attack (if not reducing confidence)
    if args.targeted and not args.reduce_confidence:
        if args.target_class is None:
            possible_targets = list(range(1000))
            possible_targets.remove(tf.argmax(image_probs[0]).numpy())
            target_class_idx = random.choice(possible_targets)
            print(f"No target class provided. Randomly selected target class index: {target_class_idx}")
        else:
            target_class_idx = args.target_class
        target_label = tf.one_hot(target_class_idx, image_probs.shape[-1])
        target_label = tf.reshape(target_label, (1, image_probs.shape[-1]))
        label_to_use = target_label
        print(f"Using targeted attack with target class index: {target_class_idx}")

    # Create adversarial example
    if args.iterative:
        print("Performing iterative FGSM attack...")
        if args.targeted and not args.reduce_confidence:
            adv_image = iterative_fgsm_attack(pretrained_model, loss_object, image, label_to_use,
                                              epsilon=args.epsilon, num_steps=args.num_steps, targeted=True)
            attack_mode = f"Iterative Targeted (eps={args.epsilon}, steps={args.num_steps})"
        else:
            adv_image = iterative_fgsm_attack(pretrained_model, loss_object, image,
                                              label_to_use if label_to_use is not None else tf.zeros_like(image_probs),
                                              epsilon=args.epsilon, num_steps=args.num_steps, targeted=False)
            mode_desc = "Confidence Reduction" if args.reduce_confidence else "Untargeted"
            attack_mode = f"Iterative {mode_desc} (eps={args.epsilon}, steps={args.num_steps})"
        filename = f'adversarial_iterative_{"targeted" if (args.targeted and not args.reduce_confidence) else "untargeted"}.png'
        display_image(pretrained_model, adv_image, attack_mode, filename, decode_predictions, output_dir)
    else:
        print("Performing one-shot FGSM attack...")
        if args.targeted and not args.reduce_confidence:
            perturbations = create_targeted_adversarial_pattern(pretrained_model, loss_object, image, label_to_use)
            adv_image = image - args.epsilon * perturbations
            attack_mode = f"One-Shot Targeted (eps={args.epsilon})"
            filename = 'adversarial_oneshot_targeted.png'
        else:
            perturbations = create_adversarial_pattern(pretrained_model, loss_object, image, label_to_use if label_to_use is not None else tf.zeros_like(image_probs))
            adv_image = image + args.epsilon * perturbations
            mode_desc = "Confidence Reduction" if args.reduce_confidence else "Untargeted"
            attack_mode = f"One-Shot {mode_desc} (eps={args.epsilon})"
            filename = 'adversarial_oneshot_untargeted.png'
        adv_image = tf.clip_by_value(adv_image, -1, 1)
        display_image(pretrained_model, adv_image, attack_mode, filename, decode_predictions, output_dir)

    print(f"All adversarial examples have been generated and saved to {output_dir}/")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
