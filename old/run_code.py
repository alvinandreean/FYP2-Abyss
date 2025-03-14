import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import tensorflow as tf

# Import pretrained models and preprocessing utilities from keras
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input as resnet_preprocess, decode_predictions as resnet_decode
from tensorflow.keras.applications.inception_v3 import InceptionV3, preprocess_input as inception_preprocess, decode_predictions as inception_decode

# Import your local cleverhans files
from fast_gradient_method import FastGradientMethod
from model import CallableModelWrapper

# For TF1-style session (cleverhans is based on TF1)
tf.compat.v1.disable_eager_execution()
sess = tf.compat.v1.Session()



# Helper functions to load and preprocess images
def load_image(image_path, target_size):
    """Load an image and resize to target_size (width, height)"""
    img = Image.open(image_path).convert('RGB')
    img = img.resize(target_size)
    img_arr = np.array(img).astype(np.float32)
    # Keep a copy for display (non-preprocessed)
    return img_arr

# Deprocessing functions to convert model inputs back to displayable images
def deprocess_resnet(x):
    """Invert ResNet50 preprocessing: add mean back and convert BGR -> RGB"""
    # In tf.keras.applications.resnet50, preprocessing does:
    #   x = x[..., ::-1] (RGB->BGR) and subtracts mean [103.939, 116.779, 123.68]
    x_copy = x.copy()
    x_copy[..., 0] += 103.939
    x_copy[..., 1] += 116.779
    x_copy[..., 2] += 123.68
    # Convert back to RGB
    x_copy = x_copy[..., ::-1]
    x_copy = np.clip(x_copy, 0, 255).astype(np.uint8)
    return x_copy

def deprocess_inception(x):
    """Invert InceptionV3 preprocessing: scale from [-1, 1] to [0, 255]"""
    x_copy = (x + 1.0) * 127.5
    x_copy = np.clip(x_copy, 0, 255).astype(np.uint8)
    return x_copy

# Load the pretrained models (from keras)
# For ResNet50, target input size is (224, 224); for InceptionV3, it is (299, 299)
resnet_model = ResNet50(weights='imagenet')
inception_model = InceptionV3(weights='imagenet')

# To get logits (pre-softmax), we create new models that output the penultimate layer.
# (This is needed because FGM in your fast_gradient_method expects logits.)
resnet_logits = tf.keras.Model(inputs=resnet_model.input, outputs=resnet_model.layers[-2].output)
inception_logits = tf.keras.Model(inputs=inception_model.input, outputs=inception_model.layers[-2].output)

# Wrap the models using your CallableModelWrapper (from your local model.py)
resnet_wrapper = CallableModelWrapper(lambda x: resnet_logits(x), output_layer="logits")
inception_wrapper = CallableModelWrapper(lambda x: inception_logits(x), output_layer="logits")

# Create placeholders for each model's input
x_resnet_ph = tf.compat.v1.placeholder(tf.float32, shape=(None, 224, 224, 3))
x_inception_ph = tf.compat.v1.placeholder(tf.float32, shape=(None, 299, 299, 3))

# Create the Fast Gradient Method attack instances
fgm_resnet = FastGradientMethod(resnet_wrapper, sess=sess)
fgm_inception = FastGradientMethod(inception_wrapper, sess=sess)

# Choose an epsilon for the perturbation (you can adjust this)
epsilon = 0.01

# Generate adversarial example symbolic tensors
x_adv_resnet = fgm_resnet.generate(x_resnet_ph, eps=epsilon)
x_adv_inception = fgm_inception.generate(x_inception_ph, eps=epsilon)

# Initialize any uninitialized variables
sess.run(tf.compat.v1.global_variables_initializer())

# ---------------------------
# Load and process a user-provided image
# Replace the following with your local image file path (or implement a file-picker)
image_path = "image\panda.jpg"  # <-- update this to your local image path

# For ResNet50
orig_img_resnet = load_image(image_path, (224, 224))
# Preprocess using ResNet50 preprocess function
img_resnet = resnet_preprocess(np.expand_dims(orig_img_resnet.copy(), axis=0))

# For InceptionV3
orig_img_inception = load_image(image_path, (299, 299))
# Preprocess using InceptionV3 preprocess function
img_inception = inception_preprocess(np.expand_dims(orig_img_inception.copy(), axis=0))

# ---------------------------
# Run the adversarial attack to obtain adversarial examples
adv_img_resnet = sess.run(x_adv_resnet, feed_dict={x_resnet_ph: img_resnet})
adv_img_inception = sess.run(x_adv_inception, feed_dict={x_inception_ph: img_inception})

# ---------------------------
# Get predictions from the original and adversarial examples
# For ResNet50, use the original keras model (which includes the softmax layer)
# Create your own placeholder:
input_resnet_ph = tf.compat.v1.placeholder(tf.float32, shape=(None, 224, 224, 3))
# Get the model's output from this placeholder:
resnet_preds = resnet_model(input_resnet_ph)
# Run the session using the new placeholder:
preds_resnet_orig = sess.run(resnet_preds, feed_dict={input_resnet_ph: img_resnet})
preds_resnet_adv = resnet_model.predict(adv_img_resnet)

# For InceptionV3
# preds_inception_orig = inception_model.predict(img_inception)
# preds_inception_adv = inception_model.predict(adv_img_inception)

# Decode predictions (top-3 for brevity)
resnet_labels_orig = resnet_decode(preds_resnet_orig, top=3)[0]
resnet_labels_adv = resnet_decode(preds_resnet_adv, top=3)[0]

# inception_labels_orig = inception_decode(preds_inception_orig, top=3)[0]
# inception_labels_adv = inception_decode(preds_inception_adv, top=3)[0]

# ---------------------------
# Invert the preprocessing for display purposes
disp_img_resnet_orig = orig_img_resnet.astype(np.uint8)  # original image is already in displayable form
disp_img_resnet_adv = deprocess_resnet(adv_img_resnet[0])
# disp_img_inception_orig = orig_img_inception.astype(np.uint8)
# disp_img_inception_adv = deprocess_inception(adv_img_inception[0])

# ---------------------------
# Helper function to plot images and predictions
def plot_results(original, adversarial, labels_orig, labels_adv, title):
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    # Construct text with label and confidence (confidence is in the third element of each tuple)
    orig_text = "\n".join([f"{lbl[1]}: {lbl[2]*100:.1f}%" for lbl in labels_orig])
    adv_text = "\n".join([f"{lbl[1]}: {lbl[2]*100:.1f}%" for lbl in labels_adv])
    
    axes[0].imshow(original)
    axes[0].set_title("Original\n" + orig_text)
    axes[0].axis('off')
    
    axes[1].imshow(adversarial)
    axes[1].set_title("Adversarial\n" + adv_text)
    axes[1].axis('off')
    
    plt.suptitle(title)
    plt.tight_layout()
    plt.show()

# ---------------------------
# Plot the results for each model
plot_results(disp_img_resnet_orig, disp_img_resnet_adv, resnet_labels_orig, resnet_labels_adv, "ResNet50 Results")
# plot_results(disp_img_inception_orig, disp_img_inception_adv, inception_labels_orig, inception_labels_adv, "InceptionV3 Results")
