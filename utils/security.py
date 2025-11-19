# utils/security.py
import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if plain password matches the hashed one"""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8") if isinstance(hashed_password, str) else hashed_password
    )

def get_password_hash(password: str) -> str:
    """Generate bcrypt hash — no 72-byte limit, works everywhere"""
    salt = bcrypt.gensalt(rounds=14)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")