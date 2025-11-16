# fix_model_real.py
import tensorflow as tf
import os

MODEL_PATH = "/home/user/Desktop/SmartFarmBackend/models/final_tomato_model.h5"
FIXED_PATH = "/home/user/Desktop/SmartFarmBackend/models/final_tomato_model_FIXED.h5"

print("Rebuilding EXACT model from your training code...")

# === EXACT SAME ARCHITECTURE ===
base_model = tf.keras.applications.MobileNetV2(
    weights='imagenet',
    include_top=False,
    input_shape=(224, 224, 3)
)
base_model.trainable = False

model = tf.keras.Sequential([
    base_model,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(256, activation='relu'),  # ← auto-named 'dense'
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(11, activation='softmax') # ← auto-named 'dense_1'
])

print("Model built. Layers:")
for layer in model.layers:
    print(f"  {layer.name}")

# === LOAD WEIGHTS BY NAME (SKIP SHAPE MISMATCH) ===
print("Loading weights by name...")
model.load_weights(MODEL_PATH, by_name=True)
print("WEIGHTS LOADED (by_name=True)")

# === SAVE CLEAN .h5 ===
model.save(FIXED_PATH)
print(f"SAVED FIXED MODEL: {FIXED_PATH}")

# === TEST ===
import numpy as np
dummy = np.random.rand(1, 224, 224, 3).astype("float32")
pred = model.predict(dummy, verbose=0)
print("Pred shape:", pred.shape)