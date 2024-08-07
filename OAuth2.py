from fastapi import Depends, HTTPException, status,Request
from fastapi.security import OAuth2PasswordBearer
from JWTtoken import verify_token
import logging
from typing import List
from models import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_data = verify_token(token, credentials_exception)
        logging.info(f"Extracted email and role from token: {token_data.email}, {token_data.role}")
        return token_data
    except Exception as e:
        logging.error(f"Error verifying token: {e}")
        raise credentials_exception

def role_required(required_roles: List[str]):
    def role_checker(token_data: TokenData = Depends(get_current_user)):
        if token_data.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return token_data
    return role_checker