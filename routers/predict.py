# routers/predict.py
import tensorflow as tf
import cv2
import numpy as np
import os
import uuid
from fastapi import APIRouter, File, UploadFile, Depends
from fastapi.responses import JSONResponse

from routers.auth import get_current_user
from models import User

router = APIRouter()

# ── LOAD MODEL ONCE (GLOBAL) ───────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "final_tomato_model.h5")

try:
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    print("MODEL LOADED FAST")
except Exception as e:
    print(f"MODEL LOAD ERROR: {e}")
    model = None

CLASSES = [
    "Bacterial_spot", "Early_blight", "Late_blight", "Leaf_Mold",
    "Septoria_leaf_spot", "Spider_mites Two-spotted_spider_mite",
    "Target_Spot", "Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato_mosaic_virus", "healthy", "powdery_mildew"
]

@router.post("/predict-plant")
async def predict_plant(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    if not model:
        return JSONResponse(status_code=500, content={"error": "Model not loaded"})

    temp_path = None
    try:
        # Save file
        temp_path = f"temp_{uuid.uuid4().hex}.jpg"
        contents = await file.read()
        with open(temp_path, "wb") as f:
            f.write(contents)

        # Read + resize FAST
        img = cv2.imread(temp_path)
        if img is None:
            raise ValueError("Invalid image")

        img = cv2.resize(img, (224, 224))  # ← FAST
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)

        # Predict
        pred = model.predict(img, verbose=0)[0]
        idx = int(np.argmax(pred))
        confidence = float(pred[idx] * 100)
        disease = CLASSES[idx]

        return {
            "disease": disease,
            "confidence": f"{confidence:.2f}%",
            "message": f"Detected {disease}."
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)