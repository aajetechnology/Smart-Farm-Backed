# save_weights_extractor.py
import tensorflow as tf
import os

# Load the broken model just to get weights
MODEL_PATH = "./models/final_tomato_model.keras"
WEIGHTS_SAVE = "./models/final_tomato_weights_only.h5"

print("Loading broken model to extract weights...")
model = tf.keras.models.load_model(MODEL_PATH, compile=False)

print("Saving clean weights only...")
model.save_weights(WEIGHTS_SAVE)
print(f"Weights saved to {WEIGHTS_SAVE}")