from fastapi import Depends, HTTPException,status,APIRouter
import database,models
from sqlmodel import Session,select
import OAuth2


router = APIRouter(
    tags=['Loan'],
    prefix='/loan'
)


@router.post('/librarian/check_overdue_loans')
def check_overdue_loans(
    db: Session = Depends(database.get_db), 
    token_data: models.TokenData = Depends(OAuth2.role_required(["Librarian"]))
    ):

    open_loans = db.exec(select(models.Loan).where(models.Loan.returned == False)).all()

    if not open_loans:
        return {"detail": "No open loans found"}

    for loan in open_loans:
        loan.check_overdue()

    db.commit()

    return {"detail": "Overdue status updated for all open loans"}


@router.post('/User/create_loan')
def create_loan(
    rent_title: str,
    db: Session = Depends(database.get_db),
    token_data: models.TokenData = Depends(OAuth2.role_required(["Member"]))
    ):
    
    user = db.exec(select(models.User).where(models.User.email == token_data.email)).first()
    
    check_book = db.exec(select(models.Book).where(models.Book.title == rent_title)).first()

    if not check_book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book '{rent_title}' not found.")
    
    if check_book.copies_available > 0:

        user_id = user.id
        book_id = check_book.id
        
        check_loan = db.exec(select(models.Loan).where(models.Loan.borrower_id == user_id,
                                                        models.Loan.borrowed_book_id == book_id
                                                        , models.Loan.returned == False)).first()
        if check_loan:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already loaned this book.")

        loan_data = models.Loan(
            borrower_id=user_id,
            borrowed_book_id=book_id
        )

        db.add(loan_data)
        db.commit()
        db.refresh(loan_data)

        loan_data.loan_requested = True

        notification = models.Notification(
            user_id=user_id,
            message=f"Loan Requested: Loan ID {loan_data.id} for Book '{rent_title}'. Waiting for librarian to approve.",
            is_read=False
        )

        db.add(notification)
        
        librarians = db.exec(select(models.User).where(models.User.role == 'Librarian')).all()

        for librarian in librarians:
            notification = models.Notification(
            user_id=librarian.id,
            message=f"Approval request for loan ID {loan_data.id} has been made by User ID : {user.id}. Please review.",
            is_read=False
        )
            
        db.add(notification)

        db.commit()

        return {"message": f"Loan request created with ID: {loan_data.id}"}
    
    if check_book.copies_available == 0:

        book_id = check_book.id

        statement = (select(models.Loan)
              .where(models.Loan.borrowed_book_id == book_id, models.Loan.returned == False)
              .order_by(models.Loan.due_date))
        
        next_available_loan = db.exec(statement).first()

        if next_available_loan:
            next_available_date = next_available_loan.due_date
            check_book.next_available_on = next_available_date

            return {"message": f"No copies available. Next available date: {next_available_date}"}
        return {"message": "Currently there are no copies of this book available with the library."}

@router.post('/User/cancel_loan')
def cancel_loan(
    loan_id: int, 
    db: Session = Depends(database.get_db), 
    token_data: models.TokenData = Depends(OAuth2.role_required(["Member"]))
    ):
    
    user = db.exec(select(models.User).where(models.User.email == token_data.email)).first()

    loan = db.exec(select(models.Loan).where(models.Loan.id == loan_id)).first()

    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found.")
    
    if loan.loan_approved:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail = " Loan has already been approved. You can't request cancellation now.")
    
    if loan.returned:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= f"You have already returned the book.")

    notification = models.Notification(
            user_id=user.id,
            message=f"Loan cancellation requested for Loan ID {loan_id}.",
            is_read=False
        )
    
    db.add(notification)

    librarians = db.exec(select(models.User).where(models.User.role == 'Librarian')).all()

    for librarian in librarians:
        notification = models.Notification(
            user_id=librarian.id,
            message=f"Cancellation request for loan ID {loan_id} has been made by User ID : {user.id}. Please review.",
            is_read=False
        )
        db.add(notification)
    loan.cancel_requested=True
    db.commit()

    return {"message": "Cancellation request sent to librarians."}

@router.post('/User/return_book')
def return_book(
    loan_id: int,
    db: Session = Depends(database.get_db),
    token_data: models.TokenData = Depends(OAuth2.role_required(["Member"]))
    ):
    
    loan = db.exec(select(models.Loan).where(models.Loan.id == loan_id)).first()

    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found.")
    
    if loan.returned:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book has already been returned.")
    
    user = db.exec(select(models.User).where(models.User.email == token_data.email)).first()
    
    if loan.borrower_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to return this book.")

    book = db.exec(select(models.Book).where(models.Book.id == loan.borrowed_book_id)).first()
    if book:
        loan.return_requested = True
        notification = models.Notification(
            user_id=user.id,
            message=f"Book return requested for Loan ID {loan_id}.",
            is_read=False
        )
        db.add(notification)

        librarians = db.exec(select(models.User).where(models.User.role == 'Librarian')).all()

        for librarian in librarians:
            notification = models.Notification(
            user_id=librarian.id,
            message=f"Return request for loan ID {loan_id} has been made by User ID : {user.id}. Please review.",
            is_read=False
        )
        db.add(notification)
        db.commit()

        return {"message": "Book return requested."}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found.")


@router.post('/librarian/approve_loan')
def approve_loan(
    request: models.LoanApprovalRequest, 
    db: Session = Depends(database.get_db), 
    token_data: models.TokenData = Depends(OAuth2.role_required(["Librarian"]))):

    loan = db.exec(select(models.Loan).where(models.Loan.id == request.loan_id)).first()
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found.")

    if loan.loan_approved:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Loan is already approved.")
    
    check_book = db.exec(select(models.Book).where(models.Book.id == loan.borrowed_book_id)).first()

    check_book.copies_available -= 1
    check_book.copies_on_rent += 1
    loan.loan_approved = True

    if request.due_date:
        loan.due_date = request.due_date

    db.add(loan)
    db.commit()
    loan = db.exec(select(models.Loan).where(models.Loan.id == request.loan_id)).first()
    
    notification = models.Notification(
        user_id=loan.borrower_id,
        message=f"Your loan request for book ID {loan.borrowed_book_id} has been approved. Please make sure you return the book by {loan.due_date} to avoid fine.",
        is_read=False
    )
    db.add(notification)
    db.commit()

    return {"message": "Loan approved successfully."}

@router.post('/librarian/cancel_loan')
def cancel_loan(
    request: models.LoanCancellationRequest,
    db: Session = Depends(database.get_db),
    token_data: models.TokenData = Depends(OAuth2.role_required(["Librarian"]))):
    

    loan = db.exec(select(models.Loan).where(models.Loan.id == request.loan_id)).first()

    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found.")

    if loan.cancel_accepted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Loan is already canceled.")
    
    loan.cancel_accepted = True
    loan.returned = True
    
    db.commit()

    notification = models.Notification(
        user_id=loan.borrower_id,
        message=f"Your loan request for book ID {loan.borrowed_book_id} has been canceled.",
        is_read=False
    )
    db.add(notification)
    db.commit()

    return {"message": "Loan canceled successfully."}

@router.post('/librarian/return_book')
def return_book(
    request: models.LoanReturnRequest,
    db: Session = Depends(database.get_db),
    token_data: models.TokenData = Depends(OAuth2.role_required(["Librarian"]))
    ):

    loan = db.exec(select(models.Loan).where(models.Loan.id == request.loan_id)).first()
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found.")

    if not loan.loan_approved or loan.returned:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Loan is not approved or has already been returned.")

    loan.returned = True
    loan.return_accepted = True
    book = db.exec(select(models.Book).where(models.Book.id == loan.borrowed_book_id)).first()
    if book:
        book.copies_available += 1
        book.copies_on_rent -= 1
        db.add(book)
    # db.add(loan)
    db.commit()

    notification = models.Notification(
        user_id=loan.borrower_id,
        message=f"Book ID {loan.borrowed_book_id} has been returned successfully.",
        is_read=False
    )
    db.add(notification)
    db.commit()

    return {"message": "Book returned successfully."}