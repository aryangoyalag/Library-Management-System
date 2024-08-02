from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from models import TokenData
import os
from dotenv import load_dotenv
import logging

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
        logging.info(f"Payload extracted from token: {payload}")
        if email is None:
            logging.warning("Email is None in token payload")
            raise credentials_exception
        token_data = TokenData(email=email)  # Ensure TokenData has an email field
        return token_data
    except JWTError as e:
        logging.error(f"JWT error: {e}")
        raise credentials_exception
