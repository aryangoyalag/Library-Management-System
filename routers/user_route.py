from fastapi import APIRouter
from fastapi import  Depends, HTTPException,status
import database,models,hashing
from sqlmodel import Session,select

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

@router.get('')
def get_user_details(db : Session = Depends(database.get_db), current_email : str = Depends(OAuth2.get_current_user)):
    user_details = db.exec(select(models.User).where(models.User.email == current_email)).first()
    loan_details_query = (
        select(models.Loan, models.Book)
        .join(models.Book, models.Loan.borrowed_book_id == models.Book.id)
        .where(models.Loan.borrower_id == user_details.id)
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
    force_logout = False
    if not hashing.Hash.verify(user.password, password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect Password.")
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    if new_password:
        user.password = hashing.Hash.bcrypt(new_password)
        # Blacklist current auth token
        force_logout = True
    
    db.commit()
    return {"User details updated."}

@router.delete('/delete_user')
def delete_user(password : str,db:Session=Depends(database.get_db),user_email:str = Depends(OAuth2.get_current_user)):
    user = db.exec(select(models.User).where(models.User.email == user_email)).first()
    if not hashing.Hash.verify(user.password, password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect Password.")
    loans = db.exec(select(models.Loan).where(models.Loan.borrower_id==user.id, models.Loan.returned==False)).all()
    if loans:
        return {"Please clear your due loans first."}
    user.delete(synchronize_session=False)
    db.commit()
    # Blacklist current auth token
    return "User deleted."
