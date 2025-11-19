# routers/predict.py
import os
import uuid
import numpy as np
import cv2
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from fastapi.responses import JSONResponse
from tensorflow.keras.models import load_model
from routers.auth import get_current_user
from models import User

# Explicit prefix to match frontend
router = APIRouter()

# ── GLOBAL MODEL (lazy load on first request) ─────────────────────
model = None
MODEL_PATH = None

def get_model():
    global model, MODEL_PATH
    if model is None:
        # This path works on Render AND local
        MODEL_PATH = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "models",
            "final_tomato_model_FIXED.h5"
        )
        print(f"Loading model from: {MODEL_PATH}")
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
        try:
            model = load_model(MODEL_PATH, compile=False)
            print("MODEL LOADED SUCCESSFULLY")
        except Exception as e:
            print(f"MODEL LOAD FAILED: {e}")
            raise RuntimeError(f"Failed to load model: {e}")
    return model

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
    # Load model only when first prediction comes
    try:
        current_model = get_model()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model error: {str(e)}")

    temp_path = None
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Save temp file
        suffix = ".jpg" if file.filename.lower().endswith(('.jpg', '.jpeg')) else ".png"
        temp_path = f"temp_{uuid.uuid4().hex}{suffix}"
        contents = await file.read()
        with open(temp_path, "wb") as f:
            f.write(contents)

        # Read and preprocess image
        img = cv2.imread(temp_path)
        if img is None:
            raise ValueError("Could not read image")

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Fix color
        img = cv2.resize(img, (224, 224))
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)  # Shape: (1, 224, 224, 3)

        # Predict
        predictions = current_model.predict(img, verbose=0)[0]
        confidence_idx = int(np.argmax(predictions))
        confidence_score = float(predictions[confidence_idx] * 100)
        disease_name = CLASSES[confidence_idx]

        return {
            "disease": disease_name,
            "confidence": f"{confidence_score:.2f}%",
            "message": f"Detected {disease_name} with {confidence_score:.1f}% confidence."
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
    finally:
        # Always clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass  # ignore cleanup errors