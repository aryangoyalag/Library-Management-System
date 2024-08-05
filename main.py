from fastapi import FastAPI, Depends, HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
import database,models,JWTtoken,hashing
from sqlmodel import Session,select
from datetime import timedelta
from routers import user_route, book_route, author_route, loan_route,notifaction_route

app = FastAPI()

database.init_db()

app.include_router(user_route.router)
app.include_router(notifaction_route.router)
app.include_router(loan_route.router)
app.include_router(book_route.router)
app.include_router(author_route.router)

@app.get('/')
def index():
    return {"Success"}

@app.post('/login')
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.exec(select(models.User).where(models.User.email == request.username)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Credential! User with {request.username} does not exist.")

    if not hashing.Hash.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect Password.")

    access_token_expires = timedelta(minutes=JWTtoken.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = JWTtoken.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# from fastapi import FastAPI
# from routers import user_route,book_route,loan_route,notifaction_route,author_route
# from starlette.middleware.wsgi import WSGIMiddleware
# import admin_interface

# app = FastAPI()

# # Include your existing routers here
# app.include_router(user_route.router)
# app.include_router(notifaction_route.router)
# app.include_router(loan_route.router)
# app.include_router(book_route.router)
# app.include_router(author_route.router)

# # Integrate the Starlette admin interface
# app.add_middleware(WSGIMiddleware, app=admin_interface.admin_app)

# @app.get('/')
# def index():
#     return {"Success"}









#Check overdue call
# Create API that checks the current date with return date and updates fine