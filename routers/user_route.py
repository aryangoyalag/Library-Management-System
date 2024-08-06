from datetime import timedelta
from fastapi import APIRouter,Query
from fastapi import  Depends, HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
import database,models,hashing,JWTtoken
from sqlmodel import Session,select,desc

import OAuth2

router = APIRouter(
    tags=['User'],
    prefix='/User'
)

# USER
# Find a way to block this api from authorised users

@router.post("/create_user")
def create_user(first_name : str,last_name : str,email :str,password : str,role:str = 'Member', db : Session = Depends(database.get_db) ):

    check_email = db.exec(select(models.User).where(models.User.email == email)).first()
    if check_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Email {email} already exists.")
    
    data = models.User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=hashing.Hash.bcrypt(password),
        role=role)

    db.add(data)
    db.commit()
    db.refresh(data)

    return {"Message" : "User created successfully." }


# Get user info 
# -> Returns User Fullname , email and list of all loans
@router.get('')
def get_user_details(
    db: Session = Depends(database.get_db),
    current_email: str = Depends(OAuth2.get_current_user),
    skip: int = Query(0, ge=0, description="Number of loans to skip"),
    limit: int = Query(10, le=100, description="Maximum number of loans to return")
):
    user_details = db.exec(select(models.User).where(models.User.email == current_email)).first()
    
    if not user_details:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
    
    loan_details_query = (
        select(models.Loan, models.Book)
        .join(models.Book, models.Loan.borrowed_book_id == models.Book.id)
        .where(models.Loan.borrower_id == user_details.id)
        .order_by(desc(models.Loan.issue_date))  # Optionally, order by issue_date in descending order
        .offset(skip)
        .limit(limit)
    )
    loan_details = db.exec(loan_details_query).all()

    loans = [
        models.LoanDetails(
            loan_id=loan.id,
            book_title=book.title,
            borrow_date=loan.issue_date,
            return_date=loan.due_date,
            loan_amount=loan.loan_amount,
            fine_amount=loan.fine,
            returned_status=loan.returned,
            overdue_status=loan.overdue
        )
        for loan, book in loan_details
    ]

    user_response = models.UserDetails(
        first_name=user_details.first_name,
        last_name=user_details.last_name,
        email=user_details.email,
        loans=loans
    )

    return user_response
@router.put('/update_user')
def update_user_details(password: str,first_name : str = None, last_name : str = None, new_password : str = None, db : Session=Depends(database.get_db),user_email:str = Depends(OAuth2.get_current_user) ):
    
    user = db.exec(select(models.User).where(models.User.email == user_email)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"user does not exit")
    
    if not hashing.Hash.verify(user.password, password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect Password.")
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    if new_password:
        user.password = hashing.Hash.bcrypt(new_password)
    
    db.commit()
    return {"User details updated."}

@router.delete('/delete_user')
def delete_user(password: str, db: Session = Depends(database.get_db), user_email: str = Depends(OAuth2.get_current_user)):
    user = db.exec(select(models.User).where(models.User.email == user_email)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"user does not exit")
    if not hashing.Hash.verify(user.password, password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect Password.")
    
    # Find all loans for the user that have not been returned
    ongoing_loans = db.exec(select(models.Loan).where(models.Loan.borrower_id == user.id)).all()
    for ongoing_loan in ongoing_loans:
        if not ongoing_loan.returned:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Clear your loans first.")
    
    # Proceed with deletion if no ongoing loans
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully."}