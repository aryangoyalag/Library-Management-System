from fastapi import FastAPI, Depends, HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
import database,models,JWTtoken,hashing
from sqlmodel import Session,select
from datetime import timedelta
from routers import user_route, book_route, author_route, loan_route,notifaction_route
from starlette_admin.contrib.sqla import Admin, ModelView
import inspect
from models import User

app = FastAPI()

database.init_db()

app.include_router(user_route.router)
app.include_router(notifaction_route.router)
app.include_router(loan_route.router)
app.include_router(book_route.router)
app.include_router(author_route.router)

classlist = ["AuthorDetails", "LoanDetails", "UserDetails","UserRole","BookCreate","AuthorCreate","AuthorUpdate","LoanApprovalRequest","LoanCancellationRequest","LoanReturnRequest","Login","Token","TokenData"]
def create_admin_view(app):
    # Create admin
    admin = Admin(database.engine, title="Library Management System")

    def get_classes_from_module():
        # Dynamicimportlibrt the module
        module =models
        
        # Filter and retrieve all classes defined in the module
        # This checks if each class is defined in the module (compares the __module__ attribute)
        classes = [member for name, member in inspect.getmembers(module, inspect.isclass)
                if member.__module__ == "models"]
        for cls in classes:
            if not cls.__name__ in classlist:
                admin.add_view(ModelView(cls))
    get_classes_from_module()
    # Mount admin to your app
    admin.mount_to(app)

create_admin_view(app)

@app.get('/')
def index():
    return {"Success"}

@app.post('/login')
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.exec(select(User).where(User.email == request.username)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Credential! User with {request.username} does not exist.")

    if not hashing.Hash.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect Password.")

    access_token_expires = timedelta(minutes=JWTtoken.ACCESS_TOKEN_EXPIRE_MINUTES)
    # Include the role in the token data
    access_token = JWTtoken.create_access_token(
        data={"sub": user.email, "role": user.role}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}