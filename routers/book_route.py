from datetime import date
from fastapi import APIRouter,Query
from fastapi import  Depends, HTTPException,status
import database,models
from sqlmodel import Session,select
import OAuth2


router = APIRouter(
    tags = ['Book'],
    prefix='/book'
)

@router.get("/search_books")
def search_books(
    title: str = Query(None, description="Filter books by title"),
    author: str = Query(None, description="Filter books by author"),
    genre: str = Query(None, description="Filter books by genre"),
    db: Session = Depends(database.get_db)
):
    query = select(models.Book)
    if title:
        query = query.where(models.Book.title.ilike(f"%{title}%"))
    
    # Filter by genre if provided
    if genre:
        query = query.where(models.Book.genre.ilike(f"%{genre}%"))
    
    # Execute the query to get books
    books = db.exec(query).all()
    
    # If an author filter is applied, further filter the results by author
    if author:
        # Find books with the specified author
        author_books_query = select(models.Book).join(models.BookAuthorAssociation).join(models.Author).where(models.Author.pen_name.ilike(f"%{author}%"))
        books = db.exec(author_books_query).all()

    return books

@router.post("/create_book")
def create_book(
    request : models.BookCreate, 
    db : Session = Depends(database.get_db),
    current_email: str = Depends(OAuth2.get_current_user)):

    check_librarian = db.exec(select(models.User).where(models.User.email==current_email)).first()

    if check_librarian.role != 'Librarian':
        raise HTTPException(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,detail=f"Access unavailable")

    if request.author_pen_names is None or not request.author_pen_names:
        author_pen_names = []
    else:
        author_pen_names = [pen_name for pen_name in request.author_pen_names if pen_name.strip()]
    
    book_data = models.Book(
        title=request.title,
        genre=request.genre,
        pages=request.pages,
        total_copies=request.total_copies,
        copies_available=request.total_copies,
        next_available_on=date.today()
    )

    db.add(book_data)
    db.commit()
    db.refresh(book_data)

    if author_pen_names:
        results = db.exec(select(models.Author).where(models.Author.pen_name.in_(author_pen_names))).fetchall()

        found_pen_names = {author.pen_name for author in results}
        requested_pen_names = set(author_pen_names)

        if not requested_pen_names.issubset(found_pen_names):
            missing_pen_names = requested_pen_names - found_pen_names
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Authors with pen names {','.join(missing_pen_names)} not found.")

        for pen_name in request.author_pen_names:
            author = db.exec(select(models.Author).where(models.Author.pen_name==pen_name)).first()
            association = models.BookAuthorAssociation(book_id=book_data.id,author_id=author.id)
            db.add(association)
        
        db.commit()

    return book_data


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