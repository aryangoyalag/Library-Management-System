from fastapi import APIRouter
from fastapi import  Depends, HTTPException,status
import database,models
from sqlmodel import Session,select
import OAuth2

router = APIRouter(
    tags=['Author'],
    prefix='/Author'
)


@router.post('/create_author')
def create_author(request : models.AuthorCreate, db : Session = Depends(database.get_db),current_email: str = Depends(OAuth2.get_current_user)):
    
    check_librarian = db.exec(select(models.User).where(models.User.email==current_email)).first()
    if check_librarian.role != 'Librarian':
        raise HTTPException(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,detail=f"Access unavailable")
    
    if request.author_books is None or not request.author_books:
        author_books = []
    else:
        author_books = [title for title in request.author_books if title.strip()]

    check_email = db.exec(select(models.User).where(models.User.email == request.email)).first()
    if check_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Email {request.email} already exists.")

    author_data = models.Author(
        pen_name=request.pen_name,
        email=request.email
    )

    db.add(author_data)
    db.commit()
    db.refresh(author_data)

    if author_books:
        books = db.exec(select(models.Book).where(models.Book.title.in_(request.author_books))).fetchall()
        found_titles = {book.title for book in books}
        requested_titles = set(request.author_books)

        if not requested_titles.issubset(found_titles):
            missing_titles = requested_titles - found_titles
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Book titles {','.join(missing_titles)} not found")
        
        
        #Associate author with book
        for title in request.author_books:
            book = db.exec(select(models.Book).where(models.Book.title==title)).first()
            association = models.BookAuthorAssociation(book_id=book.id,author_id=author_data.id)
            db.add(association)
        
        db.commit()

    return author_data

