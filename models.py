from datetime import datetime, timedelta , timezone,date
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel,EmailStr


# Create a buffer table where book : author or author : book will be added , 
# to make sure if an author or book is added later , then we can merge old books by them


class BookAuthorAssociation(SQLModel, table=True):
    book_id: int = Field(foreign_key='book.id', primary_key=True)
    author_id: int = Field(foreign_key='author.id', primary_key=True)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str = Field(nullable=False, index=True)
    last_name: str = Field(nullable=False, index=True)
    email: str = Field(nullable=False, unique=True)
    password: str = Field(nullable=False)
    role: str = Field(default='Member', nullable=False)
    loans: List["Loan"] = Relationship(back_populates='borrower')


class LoanDetails(BaseModel):
    loan_id: int
    book_title: str
    borrow_date: date
    return_date: date
    loan_amount: int
    fine_amount: int
    returned_status : bool
    overdue_status : bool

class UserDetails(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    loans: List[LoanDetails]

    class Config:
        orm_mode = True
# class UserDetails(BaseModel):
#     first_name : str
#     last_name : str
#     email : EmailStr
#     role : str
#     loans = List[str]

#     class Config:
#         orm_mode = True

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(nullable=False, index=True)
    genre: Optional[str] = Field(nullable=True, index=True)
    pages: Optional[int] = Field(nullable=True)
    total_copies: int = Field(nullable=False)
    copies_available: Optional[int] = Field(nullable=True)
    copies_on_rent: int = Field(default=0, nullable=False)
    next_available_on: Optional[date] = Field(default=None)
    authors: List["Author"] = Relationship(back_populates='books',link_model=BookAuthorAssociation)
    loans: List["Loan"] = Relationship(back_populates='borrowed_book')

class BookCreate(BaseModel):
    title : str
    genre: Optional[str] = None
    pages: Optional[int] = None
    total_copies: int 
    author_pen_names : List[str] = None


class Author(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pen_name: str = Field(nullable=False, index=True)
    email: str = Field(nullable=False, unique=True)
    books: List["Book"] = Relationship(back_populates='authors',link_model=BookAuthorAssociation)

    @property
    def bibliography(self):
        return [book.title for book in self.books]

class AuthorCreate(BaseModel):
    pen_name : str
    email : EmailStr
    author_books : List[str]

class Loan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    borrower_id: int = Field(foreign_key='user.id', nullable=False)
    borrowed_book_id: int = Field(foreign_key='book.id', nullable=False)
    issue_date: date = Field(default_factory=lambda: date.today(), nullable=False)
    due_date: date = Field(nullable=False)
    returned: bool = Field(default=False)
    overdue: bool = Field(default=False)
    loan_amount: int = Field(default=50, nullable=False)
    fine: int = Field(default=0)

    borrower: User = Relationship(back_populates='loans')
    borrowed_book: Book = Relationship(back_populates='loans')

    def __init__(self, borrower_id: int, borrowed_book_id: int):
        super().__init__(borrower_id=borrower_id, borrowed_book_id=borrowed_book_id)
        self.issue_date = date.today()
        self.due_date = self.issue_date + timedelta(days=15)

    def check_overdue(self):
        if not self.returned and date.today() > self.due_date.date():
            self.overdue = True
            days_overdue = (date.today() - self.due_date.date()).days
            self.fine = days_overdue * 10
        else:
            self.overdue = False
            self.fine = 0

    def return_book(self):
        self.returned = True
        self.check_overdue()

class Login(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    