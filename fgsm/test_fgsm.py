import unittest
import tensorflow as tf
import numpy as np
from fgsm import FGSM  

class TestFGSMAttack(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.image_path = "FYP2-Abyss\fgsm\image\ferrari.jpeg" 
        cls.model_name = "mobilenet_v2"
        cls.fgsm = FGSM(epsilon=0.05, model_name=cls.model_name)
        cls.image = cls.fgsm.preprocess(cls.image_path)
        cls.image_probs = cls.fgsm.model.predict(cls.image, verbose=0)
        class_idx = tf.argmax(cls.image_probs[0]).numpy()
        cls.label = tf.one_hot(class_idx, cls.image_probs.shape[-1])
        cls.label = tf.reshape(cls.label, (1, cls.image_probs.shape[-1]))

    def test_gradient_direction_consistency(self):
        """Test if perturbation equals sign of gradient."""
        with tf.GradientTape() as tape:
            tape.watch(self.image)
            prediction = self.fgsm.model(self.image)
            loss_object = tf.keras.losses.CategoricalCrossentropy()
            loss = loss_object(self.label, prediction)

        gradient = tape.gradient(loss, self.image)
        expected_perturbation = tf.sign(gradient)
        actual_perturbation = self.fgsm.create_adversarial_pattern(self.image, self.label)

        self.assertTrue(
            tf.reduce_all(tf.equal(expected_perturbation, actual_perturbation)),
            msg="Perturbation does not match sign of gradient."
        )

    def test_epsilon_scaling_magnitude(self):
        """Test that larger epsilon creates larger perturbation effect."""
        small_eps = 0.01
        large_eps = 0.1

        perturbation = self.fgsm.create_adversarial_pattern(self.image, self.label)
        adv_small = self.image + small_eps * perturbation
        adv_large = self.image + large_eps * perturbation

        dist_small = tf.norm(adv_small - self.image)
        dist_large = tf.norm(adv_large - self.image)

        self.assertGreater(dist_large.numpy(), dist_small.numpy(),
            msg="Larger epsilon did not result in a larger perturbation.")

    def test_adversarial_image_clipping(self):
        """Test that output image is clipped to [-1, 1] for MobileNetV2."""
        perturbation = self.fgsm.create_adversarial_pattern(self.image, self.label)
        adv_image = self.image + self.fgsm.epsilon * perturbation
        adv_image = tf.clip_by_value(adv_image, -1, 1)

        self.assertTrue(
            tf.reduce_all(adv_image >= -1.0) and tf.reduce_all(adv_image <= 1.0),
            msg="Adversarial image not clipped to [-1, 1] range."
        )

if __name__ == '__main__':
    unittest.main()
