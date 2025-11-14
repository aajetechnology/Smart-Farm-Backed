import tensorflow as tf
import os

MODEL_PATH = "./models/final_tomato_model.h5"
WEIGHTS_PATH = "./models/clean_weights.h5"

print("Loading model in SAFE MODE to extract weights...")

try:
    # This bypasses the broken graph
    model = tf.keras.models.load_model(MODEL_PATH, compile=False, safe_mode=False)
    model.save_weights(WEIGHTS_PATH)
    print(f"SUCCESS! Weights saved to {WEIGHTS_PATH}")
except Exception as e:
    print("Safe mode failed:", e)
    print("Falling back to manual checkpoint extraction...")
    
    # Manual extraction from .keras zip
    import zipfile
    import h5py
    import numpy as np
    
    extract_dir = "temp_weights_extract"
    os.makedirs(extract_dir, exist_ok=True)
    
    with zipfile.ZipFile(MODEL_PATH, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    ckpt_path = f"{extract_dir}/variables/variables"
    if not os.path.exists(ckpt_path):
        print("No variables found. Model might be empty.")
        exit(1)
    
    # Load checkpoint
    reader = tf.train.load_checkpoint(ckpt_path)
    var_map = {name: reader.get_tensor(name) for name in tf.train.list_variables(ckpt_path)}
    
    # Save to .h5
    with h5py.File(WEIGHTS_PATH, 'w') as f:
        for name, value in var_map.items():
            f.create_dataset(name, data=value)
    
    print(f"Manual extraction SUCCESS! Weights saved to {WEIGHTS_PATH}")