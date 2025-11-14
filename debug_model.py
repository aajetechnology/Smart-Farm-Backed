# debug_model.py (FINAL VERSION)
import tensorflow as tf
import os

def create_tomato_model():
    # INPUT
    inputs = tf.keras.Input(shape=(224, 224, 3), name="input_image")

    # PREPROCESSING (this was missing!)
    x = tf.keras.layers.Normalization(
        mean=[123.68, 116.779, 103.939],
        variance=[58.393**2, 57.12**2, 57.375**2],
        name="normalization"
    )(inputs)

    # BACKBONE
    base = tf.keras.applications.EfficientNetB0(
        include_top=False,
        weights=None,  # we'll load
        input_tensor=x
    )

    x = base.output

    # POOLING
    gap = tf.keras.layers.GlobalAveragePooling2D()(x)
    gmp = tf.keras.layers.GlobalMaxPooling2D()(x)

    # MERGE — THIS WAS THE BUG!
    merged = tf.keras.layers.Concatenate()([gap, gmp])
    # OR: merged = tf.keras.layers.Add()([gap, gmp])

    # CLASSIFIER
    x = tf.keras.layers.Dense(512, activation='relu', name="dense")(merged)
    x = tf.keras.layers.Dropout(0.5)(x)
    outputs = tf.keras.layers.Dense(10, activation='softmax', name="dense_1")(x)  # CHANGE 10

    return tf.keras.Model(inputs=inputs, outputs=outputs)

# === LOAD WEIGHTS ===
WEIGHTS_PATH = "./models/final_tomato_model.h5"

print("Creating correct model...")
model = create_tomato_model()

print(f"Loading clean weights from: {WEIGHTS_PATH}")
model.load_weights(WEIGHTS_PATH)

print("Model loaded successfully!")

# === INSPECT ===
print("\nInputs:", len(model.inputs))
for i, inp in enumerate(model.inputs):
    print(f"  Input {i}: {inp.shape}, name: {inp.name}")

print("Outputs:", len(model.outputs))
for i, out in enumerate(model.outputs):
    print(f"  Output {i}: {out.shape}, name: {out.name}")

# === TEST ===
import numpy as np
img = np.random.rand(1, 224, 224, 3).astype("float32")
pred = model.predict(img)
print("\nPrediction shape:", pred.shape)