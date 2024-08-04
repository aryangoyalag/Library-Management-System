from fastapi import FastAPI, Depends, HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
import database,models,JWTtoken,hashing
from sqlmodel import Session,select
from datetime import date,timedelta
import OAuth2
from routers import user_route, book_route, author_route
app = FastAPI()

database.init_db()

app.include_router(user_route.router)
app.include_router(book_route.router)
app.include_router(author_route.router)

@app.get('/')
def index():
    return {"Success"}

# LOGIN

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

# LOAN

@app.post('/create_loan')
def create_loan(rent_title : str, db : Session = Depends(database.get_db),current_email: str = Depends(OAuth2.get_current_user)):

    check_librarian = db.exec(select(models.User).where(models.User.email==current_email)).first()
    
    if check_librarian.role != 'Member':
        raise HTTPException(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,detail=f"Access unavailable")
    check_book = db.exec(select(models.Book).where(models.Book.title == rent_title)).first()
    if not check_book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Book {rent_title} not found.")
    if check_book.copies_available > 0:
        user_id = check_librarian.id
        book_id = check_book.id
        
        check_loan = db.exec(select(models.Loan).where(models.Loan.borrower_id==user_id,models.Loan.borrowed_book_id==book_id,models.Loan.returned==False)).first()
        if check_loan:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"You have already loaned this book.")

        check_book.copies_available = check_book.copies_available - 1
        check_book.copies_on_rent = check_book.copies_on_rent + 1

        loan_data = models.Loan(
            borrower_id=user_id,
            borrowed_book_id=book_id
        )
        db.add(loan_data)
        db.commit()
        db.refresh(loan_data)

        return f"Loan created id : {loan_data.id} "
    
    if check_book.copies_available == 0:
        book_id = check_book.id
        next_available_loan = db.exec(select(models.Loan).where(models.Loan.borrowed_book_id == book_id, models.Loan.returned == False).order_by(models.Loan.due_date)).first()
        if next_available_loan:
            next_available_date = next_available_loan.due_date
            return {"message": f"No copies available. Next available date: {next_available_date}"}
        return {"Currently there are no copies of this book available with the library."}



 

# Delete loan api 
# -> to be used when user created loan by mistake but will be approved by lirarian 
# Librarian gets notified when user requests loan cancelation which is then approved by Librarian

# Book return api
# When user returns the book they notify librarian which he then approves

# User notification
# User gets notfication about upcoming return date for their loan 3 days prior

#Check overdue call
# Create API that checks the current date with return date and updates fine