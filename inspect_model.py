# inspect_model.py
import h5py
import json

MODEL_PATH = "/home/user/Desktop/SmartFarmBackend/models/final_tomato_model.h5"

with h5py.File(MODEL_PATH, 'r') as f:
    print("=== LAYERS IN .h5 ===")
    for name in f.keys():
        if name != 'model_weights':
            print(f"Group: {name}")
        else:
            print("Layers with weights:")
            for layer_name in f['model_weights'].keys():
                print(f"  - {layer_name}")
    
    # Try to get model config
    if 'model_config' in f.attrs:
        config = f.attrs['model_config']
        if isinstance(config, bytes):
            config = config.decode('utf-8')
        try:
            model_json = json.loads(config)
            print("\n=== MODEL CONFIG ===")
            print(json.dumps(model_json, indent=2)[:1000])  # first 1000 chars
        except:
            print("Could not parse model_config")