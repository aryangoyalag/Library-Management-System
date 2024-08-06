from datetime import date
from fastapi import APIRouter,Query
from fastapi import  Depends, HTTPException,status
import database,models
from sqlmodel import Session,select,and_
import OAuth2
from typing import Optional


router = APIRouter(
    tags = ['Book'],
    prefix='/book'
)
@router.get("/search_books")
def search_books(
    title: Optional[str] = Query(None, description="Filter books by title"),
    author: Optional[str] = Query(None, description="Filter books by author"),
    genre: Optional[str] = Query(None, description="Filter books by genre"),
    db: Session = Depends(database.get_db),
    skip: int = Query(0, ge=0, description="Number of books to skip"),
    limit: int = Query(10, le=100, description="Maximum number of books to return")
):
    query = select(models.Book)
    
    # Apply title filter if provided
    if title:
        query = query.where(models.Book.title.ilike(f"%{title}%"))
    
    # Apply genre filter if provided
    if genre:
        query = query.where(models.Book.genre.ilike(f"%{genre}%"))
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Fetch books based on title, genre, and pagination
    books = db.exec(query).all()
    
    # If an author filter is applied, further filter the results by author
    if author:
        # Adjust the query to include books associated with the specified author
        author_books_query = (
            select(models.Book)
            .join(models.BookAuthorAssociation)
            .join(models.Author)
            .where(and_(models.Author.pen_name.ilike(f"%{author}%"),
                        models.Book.id.in_([book.id for book in books])))
            .offset(skip)
            .limit(limit)
        )
        books = db.exec(author_books_query).all()
    
    return books


@router.delete('/delete_book/{id}')
def delete_book(
    id: int,
    db: Session = Depends(database.get_db),
    user: str = Depends(OAuth2.get_current_user)
):
    user_details = db.exec(select(models.User).where(models.User.email == user)).first()

    if user_details.role != 'Librarian':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access unavailable"
        )
    
    book = db.exec(select(models.Book).where(models.Book.id == id)).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {id} not found."
        )
    
    check_loans = db.exec(
        select(models.Loan).where(
            models.Loan.borrowed_book_id == id,
            models.Loan.returned == False
        )
    ).all()
    
    if check_loans:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Please clear the loans on Book id {id} first."
        )
    
    # Remove associations related to the book
    associations = db.exec(select(models.BookAuthorAssociation).where(models.BookAuthorAssociation.book_id == id)).all()
    for association in associations:
        db.delete(association)
    
    # Delete the book
    db.delete(book)
    db.commit()
    
    return {"message": "Book and its associations deleted successfully."}

@router.put('/update_book/{id}')
def update_book(id:int,
                title:str=None,
                pages:int=None,
                total_copies:int=None,
                db:Session=Depends(database.get_db),
                user:str=Depends(OAuth2.get_current_user)):
    
    user_details = db.exec(select(models.User).where(models.User.email==user)).first()

    if user_details.role != 'Librarian':
        raise HTTPException(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,detail=f"Access unavailable")
    
    book = db.exec(select(models.Book).where(models.Book.id==id)).first()

    if title:
        book.title = title
    if pages:
        book.pages = pages
    if total_copies:
        book.total_copies = total_copies
    
    db.commit()
    return {"Book details have been updated."}