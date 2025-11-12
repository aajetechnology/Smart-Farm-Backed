from fastapi import APIRouter

router = APIRouter()

@router.post("/predict-plant")
def predict_plant():
    return {"message": "Predict plant endpoint (to be implemented)"}