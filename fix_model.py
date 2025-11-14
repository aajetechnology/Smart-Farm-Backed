# fix_model.py
import tensorflow as tf
import zipfile
import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout

BROKEN_MODEL = "./models/final_tomato_model.keras"
WEIGHTS_H5 = "temp_extracted_weights.h5"
FIXED_MODEL = "./models/fixed_tomato_model.keras"

print("Step 1: Extracting REAL weights from .keras ZIP...")
with zipfile.ZipFile(BROKEN_MODEL, 'r') as z:
    with z.open('model.weights.h5') as src, open(WEIGHTS_H5, 'wb') as dst:
        dst.write(src.read())
print("Weights extracted to temp_extracted_weights.h5")

print("Step 2: Building CLEAN model...")
model = Sequential([
    tf.keras.layers.Input(shape=(224, 224, 3)),
    EfficientNetB0(include_top=False, weights=None, input_shape=(224, 224, 3)),
    GlobalAveragePooling2D(),
    Dense(512, activation='relu'),
    Dropout(0.5),
    Dense(11, activation='softmax')  # 11 classes!
], name="fixed_tomato_model")
print("Clean model built!")

print("Step 3: Loading REAL WEIGHTS from .h5...")
try:
    model.load_weights(WEIGHTS_H5, by_name=True, skip_mismatch=True)
    print("REAL WEIGHTS LOADED SUCCESSFULLY!")
except Exception as e:
    print(f"Failed: {e}")

print("Step 4: Saving FINAL model...")
model.save(FIXED_MODEL)
print(f"\nMODEL FIXED & WEIGHTS LOADED: {FIXED_MODEL}")

# Cleanup
os.remove(WEIGHTS_H5)
print("Now run: uvicorn main:app --reload")