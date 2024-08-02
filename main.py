from fastapi import FastAPI, Depends, HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
import database,models,JWTtoken,hashing
from sqlmodel import Session,select
from datetime import date,timedelta
import OAuth2

app = FastAPI()

database.init_db()


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

@app.post("/create_user")
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

@app.post("/create_book")
def create_book(request : models.BookCreate, db : Session = Depends(database.get_db),current_email: str = Depends(OAuth2.get_current_user)):
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
        #Associate book with authors

        for pen_name in request.author_pen_names:
            author = db.exec(select(models.Author).where(models.Author.pen_name==pen_name)).first()
            association = models.BookAuthorAssociation(book_id=book_data.id,author_id=author.id)
            db.add(association)
        
        db.commit()

    return book_data


@app.post('/create_author')
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

@app.post('/create_loan')
def create_loan(request : models.LoanCreate, db : Session = Depends(database.get_db),current_email: str = Depends(OAuth2.get_current_user)):
    pass