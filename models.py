from datetime import datetime, timedelta, date
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel, EmailStr
from enum import Enum

class BookAuthorAssociation(SQLModel, table=True):
    book_id: Optional[int] = Field(foreign_key='book.id', primary_key=True, nullable=True)
    author_id: Optional[int] = Field(foreign_key='author.id', primary_key=True, nullable=True)

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(nullable=False, index=True)
    genre: Optional[str] = Field(nullable=True, index=True)
    pages: Optional[int] = Field(nullable=True)
    total_copies: int = Field(nullable=False,ge=0)
    copies_available: Optional[int] = Field(nullable=True,ge=0)
    copies_on_rent: int = Field(default=0, nullable=False,ge=0)
    next_available_on: Optional[date] = Field(default=None)
    authors: List["Author"] = Relationship(back_populates='books', link_model=BookAuthorAssociation)
    loans: List["Loan"] = Relationship(back_populates='borrowed_book')

class Author(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pen_name: str = Field(nullable=False, index=True)
    email: str = Field(nullable=False, unique=True)
    books: List["Book"] = Relationship(back_populates='authors', link_model=BookAuthorAssociation)

class AuthorDetails(BaseModel):
    pen_name: str
    email: EmailStr
    books: List[str] = []

    class Config:
        orm_mode = True


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str = Field(nullable=False, index=True)
    last_name: str = Field(nullable=False, index=True)
    email: str = Field(nullable=False, unique=True)
    password: str = Field(nullable=False)
    role: str = Field(default='Member', nullable=False)
    loans: List["Loan"] = Relationship(back_populates='borrower', sa_relationship_kwargs={"cascade": "all, delete-orphan"})

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
    loan_requested: Optional[bool] = Field(default=False)
    loan_approved: Optional[bool] = Field(default=False)
    return_requested: Optional[bool] = Field(default=False)
    return_accepted: Optional[bool] = Field(default=False)
    cancel_requested: Optional[bool] = Field(default=False)
    cancel_accepted: Optional[bool] = Field(default=False)

    borrower: User = Relationship(back_populates='loans')
    borrowed_book: Book = Relationship(back_populates='loans')

    def __init__(self, borrower_id: int, borrowed_book_id: int):
        self.borrower_id = borrower_id
        self.borrowed_book_id = borrowed_book_id
        self.issue_date = date.today()
        self.due_date = self.issue_date + timedelta(days=15)

    def check_overdue(self):
        if not self.returned and date.today() > self.due_date:
            self.overdue = True
            days_overdue = (date.today() - self.due_date).days
            self.fine = days_overdue * 10
        else:
            self.overdue = False
            self.fine = 0

    def return_book(self):
        self.returned = True
        self.check_overdue()

class LoanDetails(BaseModel):
    loan_id: int
    book_title: str
    borrow_date: date
    return_date: date
    loan_amount: int
    fine_amount: int
    returned_status: bool
    overdue_status: bool

class UserDetails(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    loans: List[LoanDetails]

    class Config:
        orm_mode = True

class BookCreate(BaseModel):
    title: str
    genre: Optional[str] = None
    pages: Optional[int] = None
    total_copies: int 
    author_pen_names: List[str] = None

class AuthorCreate(BaseModel):
    pen_name: str
    email: EmailStr
    author_books: List[str]

class AuthorUpdate(BaseModel):
    pen_name: Optional[str] = None
    email: Optional[EmailStr] = None
    
class LoanApprovalRequest(BaseModel):
    loan_id: int
    due_date: Optional[date] = None

class LoanCancellationRequest(BaseModel):
    loan_id: int

class LoanReturnRequest(BaseModel):
    loan_id: int

class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    message: str
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Login(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str
    role: str