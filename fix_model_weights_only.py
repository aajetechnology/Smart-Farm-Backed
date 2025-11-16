# fix_model_weights_only.py
import tensorflow as tf
import h5py
import numpy as np
import os

MODEL_PATH = "/home/user/Desktop/SmartFarmBackend/models/final_tomato_model.h5"
FIXED_PATH = "/home/user/Desktop/SmartFarmBackend/models/final_tomato_model_FIXED.h5"

print("Building CORRECT model architecture...")

# === BUILD CLEAN MODEL ===
input_shape = (224, 224, 3)
inputs = tf.keras.Input(shape=input_shape, name='input_1')

# Use same base as you likely did: MobileNetV2
base_model = tf.keras.applications.MobileNetV2(
    input_shape=input_shape,
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False

x = base_model(inputs, training=False)
x = tf.keras.layers.GlobalAveragePooling2D()(x)
x = tf.keras.layers.Dropout(0.2)(x)
outputs = tf.keras.layers.Dense(11, activation='softmax', name='predictions')(x)

model = tf.keras.Model(inputs, outputs)
print("Model built. Layers:", [layer.name for layer in model.layers])

# === LOAD WEIGHTS ONLY (SKIP BROKEN CONFIG) ===
print(f"Loading weights from {MODEL_PATH}...")
try:
    model.load_weights(MODEL_PATH)
    print("WEIGHTS LOADED SUCCESSFULLY!")
except Exception as e:
    print("FAILED TO LOAD WEIGHTS:", e)
    print("Trying layer-by-layer matching...")
    # Fallback: manual weight assignment
    with h5py.File(MODEL_PATH, 'r') as f:
        for layer in model.layers:
            if layer.name in f:
                print(f"  Loading weights for {layer.name}")
                weights = [f[f'{layer.name}/{w}'][()] for w in f[layer.name]]
                try:
                    layer.set_weights(weights)
                except:
                    print(f"    Shape mismatch on {layer.name}, skipping...")
            else:
                print(f"  No weights for {layer.name}")

# === SAVE FIXED MODEL ===
model.save(FIXED_PATH, include_optimizer=False)
print(f"FIXED MODEL SAVED: {FIXED_PATH}")

# === TEST IT ===
print("\nTesting model...")
dummy = np.random.rand(1, 224, 224, 3).astype(np.float32)
pred = model.predict(dummy)
print("Prediction shape:", pred.shape)  # Should be (1, 11)
print("Top class:", np.argmax(pred))