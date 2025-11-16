# fix_model_perfect.py
import tensorflow as tf
import numpy as np
import os

MODEL_PATH = "/home/user/Desktop/SmartFarmBackend/models/final_tomato_model.h5"
FIXED_PATH = "/home/user/Desktop/SmartFarmBackend/models/final_tomato_model_FIXED.h5"

print("Building EXACT model from inspection...")

# Sequential model
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(224, 224, 3)),
    
    # MobileNetV2 base (frozen)
    tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights=None  # We'll load
    ),
    
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dropout(0.2),
    
    # Hidden dense
    tf.keras.layers.Dense(128, activation='relu', name='dense'),  # ← match name
    # Final output
    tf.keras.layers.Dense(11, activation='softmax', name='dense_1')  # ← match name
])

# Freeze base
model.layers[1].trainable = False

print("Model layers:")
for i, layer in enumerate(model.layers):
    print(f"  [{i}] {layer.name} → trainable: {layer.trainable}")

# Load weights by name
print(f"Loading weights from {MODEL_PATH}...")
model.load_weights(MODEL_PATH, by_name=True)
print("WEIGHTS LOADED PERFECTLY!")

# Save fixed
model.save(FIXED_PATH)
print(f"SAVED: {FIXED_PATH}")

# Test
dummy = np.random.rand(1, 224, 224, 3).astype("float32")
pred = model.predict(dummy, verbose=0)
print("Output shape:", pred.shape)
print("Top class:", np.argmax(pred))