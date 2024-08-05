from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from models import TokenData
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("KEY")
ALGORITHM = os.getenv("ALGO")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))  
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        
        return TokenData(email=email)
    except jwt.PyJWTError:
        raise credentials_exception