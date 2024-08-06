from fastapi import APIRouter,Query
from fastapi import  Depends, HTTPException,status
import database,models
from sqlmodel import Session,select,desc
import OAuth2
from typing import List
router = APIRouter(
    tags=['Author'],
    prefix='/Author'
)

@router.get('/search_by_pen_name', response_model=List[models.AuthorDetails])
def search_by_pen_name(
    pen_name: str,
    db: Session = Depends(database.get_db),
    skip: int = Query(0, ge=0, description="Number of authors to skip"),
    limit: int = Query(10, le=100, description="Maximum number of authors to return")
):
    # Fetch authors matching the provided pen name with pagination
    statement = (select(models.Author)
                 .where(models.Author.pen_name.ilike(f"%{pen_name}%"))
                 .offset(skip)
                 .limit(limit))
    authors = db.exec(statement).all()
    
    if not authors:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No authors found with the given pen name")
    
    # Prepare the list of author details
    author_details_list = []
    for author in authors:
        # Fetch the books associated with the author
        books = db.exec(select(models.Book)
                        .join(models.BookAuthorAssociation)
                        .where(models.BookAuthorAssociation.author_id == author.id)).all()
        book_titles = [book.title for book in books]
        
        author_details_list.append(models.AuthorDetails(
            pen_name=author.pen_name,
            email=author.email,
            books=book_titles
        ))
    
    return author_details_list

@router.post('/create_author')
def create_author(request : models.AuthorCreate, db : Session = Depends(database.get_db),current_email: str = Depends(OAuth2.get_current_user)):
   # This api is not returning anything 
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

@router.put('/update_author/{author_id}')
def update_author(author_id: int, request: models.AuthorUpdate, db: Session = Depends(database.get_db), current_email: str = Depends(OAuth2.get_current_user)):
    check_librarian = db.exec(select(models.User).where(models.User.email == current_email)).first()
    if check_librarian.role != 'Librarian':
        raise HTTPException(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, detail="Access unavailable")

    author = db.exec(select(models.Author).where(models.Author.id == author_id)).first()
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author with ID {author_id} not found")

    # Update author details
    if request.pen_name:
        author.pen_name = request.pen_name
    if request.email:
        author.email = request.email

    db.commit()

    return author

@router.delete('/delete_author/{author_id}')
def delete_author(author_id: int, db: Session = Depends(database.get_db), current_email: str = Depends(OAuth2.get_current_user)):
    check_librarian = db.exec(select(models.User).where(models.User.email == current_email)).first()
    if check_librarian.role != 'Librarian':
        raise HTTPException(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, detail="Access unavailable")

    author = db.exec(select(models.Author).where(models.Author.id == author_id)).first()
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Author with ID {author_id} not found")

    # Delete associations first to avoid foreign key constraint issues
    associations = db.exec(select(models.BookAuthorAssociation).where(models.BookAuthorAssociation.author_id == author_id)).all()
    for association in associations:
        db.delete(association)
    # Delete author
    db.delete(author)
    db.commit()

    return {"detail": "Author deleted successfully"}