import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.models import Sequential

# Your exact classes
CLASSES = [
    'Bacterial_spot', 'Early_blight', 'Late_blight', 'Leaf_Mold', 
    'Septoria_leaf_spot', 'Spider_mites Two-spotted_spider_mite', 
    'Target_Spot', 'Tomato_Yellow_Leaf_Curl_Virus', 'Tomato_mosaic_virus', 
    'healthy', 'powdery_mildew'
]

def create_fixed_model():
    """Create FIXED MobileNetV2 model that matches your training"""
    
    base_model = MobileNetV2(
        weights='imagenet',
        include_top=False,
        input_shape=(224, 224, 3)
    )
    
    # ✅ FIXED ARCHITECTURE - Single tensor flow
    model = Sequential([
        base_model,
        GlobalAveragePooling2D(),  # ← THIS FIXES THE 2-TENSOR ISSUE!
        Dropout(0.2),
        Dense(128, activation='relu'),
        Dropout(0.2),
        Dense(len(CLASSES), activation='softmax')  # 11 classes
    ])
    
    return model

# Create and save FIXED model
model = create_fixed_model()
model.save('models/final_tomato_model.keras')
print("✅ FIXED MODEL SAVED! Ready to use.")