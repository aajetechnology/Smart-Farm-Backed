# fix_model_final.py
import tensorflow as tf
import os

MODEL_PATH = "/home/user/Desktop/SmartFarmBackend/models/final_tomato_model.h5"
FIXED_PATH = "/home/user/Desktop/SmartFarmBackend/models/final_tomato_model_FIXED.h5"

print("Building EXACT model (3 weighted layers)...")

inputs = tf.keras.Input(shape=(224, 224, 3))

# Base
base = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights=None  # We'll load manually
)(inputs)

# Pool
x = tf.keras.layers.GlobalAveragePooling2D()(base)

# Output
outputs = tf.keras.layers.Dense(11, activation='softmax')(x)

model = tf.keras.Model(inputs, outputs)

print("Model layers (weighted):")
for layer in model.layers:
    if layer.weights:
        print(f"  {layer.name}")

# Load weights by name
print(f"Loading weights from {MODEL_PATH}...")
model.load_weights(MODEL_PATH, by_name=True)
print("WEIGHTS LOADED BY NAME!")

# Save
model.save(FIXED_PATH)
print(f"SAVED FIXED MODEL: {FIXED_PATH}")

# Test
import numpy as np
dummy = np.random.rand(1, 224, 224, 3).astype("float32")
pred = model.predict(dummy)
print("Output shape:", pred.shape)
print("Top class:", np.argmax(pred))