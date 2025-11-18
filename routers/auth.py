# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import EmailStr
import os
import shutil
from dotenv import load_dotenv
from database import get_db
from models import User
from routers.schemas import UserIn, UserOut, Token, LoginResponse  # ← ADD LoginResponse

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY must be set in .env file")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login/")



def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print(f"Raw token received: {token}")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        print(f"Decoded email: {email}")
        if email is None:
            raise credentials_exception
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise credentials_exception
        return user
    except JWTError as e:
        print(f"JWT Error: {e}")
        raise credentials_exception


@router.post("/register", response_model=UserOut)
async def register(
    email: EmailStr = Form(...),
    username: str = Form(...),
    full_name: str = Form(None),
    password: str = Form(...),
    confirm_password: str = Form(...),
    profile_pic: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    profile_pic_path = None
    if profile_pic:
        upload_dir = os.getenv("UPLOAD_DIR", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, profile_pic.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(profile_pic.file, buffer)
        profile_pic_path = file_path

    hashed_password = pwd_context.hash(password)
    new_user = User(
        email=email,
        username=username,
        full_name=full_name,
        profile_pic=profile_pic_path,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# UPDATED: Return user in login response
@router.post("/login", response_model=LoginResponse, include_in_schema=True)
@router.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    print(f"Login attempt for: {form_data.username}")
    user = db.query(User).filter(
        (User.email == form_data.username) | (User.username == form_data.username)
    ).first()

    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        print("Invalid credentials")
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode(
        {"sub": user.email, "exp": datetime.utcnow() + access_token_expires},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    print(f"Token generated for {user.email}")

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserOut.from_orm(user)  # ← RETURN FULL USER
    }