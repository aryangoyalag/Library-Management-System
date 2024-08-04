from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from JWTtoken import verify_token
import logging

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_data = verify_token(token, credentials_exception)
        logging.info(f"Extracted email from token: {token_data.email}")
        return token_data.email
    except Exception as e:
        logging.error(f"Error verifying token: {e}")
        raise credentials_exception