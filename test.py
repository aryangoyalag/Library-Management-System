from datetime import datetime, timedelta , timezone
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


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

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(nullable=False, index=True)
    genre: Optional[str] = Field(nullable=True, index=True)
    pages: Optional[int] = Field(nullable=True)
    total_copies: int = Field(nullable=False)
    copies_available: Optional[int] = Field(nullable=True)
    copies_on_rent: int = Field(default=0, nullable=False)
    next_available_on: Optional[datetime] = Field(default=None)
    authors: List["Author"] = Relationship(back_populates='books',link_model=BookAuthorAssociation)
    loans: List["Loan"] = Relationship(back_populates='borrowed_book')

class Author(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pen_name: str = Field(nullable=False, index=True)
    email: str = Field(nullable=False, unique=True)
    books: List[Book] = Relationship(back_populates='authors',link_model=BookAuthorAssociation)

    @property
    def bibliography(self):
        return [book.title for book in self.books]

class Loan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    borrower_id: int = Field(foreign_key='user.id', nullable=False)
    borrowed_book_id: int = Field(foreign_key='book.id', nullable=False)
    issue_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    due_date: datetime = Field(nullable=False)
    returned: bool = Field(default=False)
    overdue: bool = Field(default=False)
    loan_amount: int = Field(default=50, nullable=False)
    fine: int = Field(default=0)

    borrower: User = Relationship(back_populates='loans')
    borrowed_book: Book = Relationship(back_populates='loans')

    def __init__(self, borrower_id: int, borrowed_book_id: int):
        super().__init__(borrower_id=borrower_id, borrowed_book_id=borrowed_book_id)
        self.issue_date = datetime.now(timezone.utc)
        self.due_date = self.issue_date + timedelta(days=15)

    def check_overdue(self):
        if not self.returned and datetime.now(timezone.utc).date() > self.due_date.date():
            self.overdue = True
            days_overdue = (datetime.now(timezone.utc).date() - self.due_date.date()).days
            self.fine = days_overdue * 10
        else:
            self.overdue = False
            self.fine = 0

    def return_book(self):
        self.returned = True
        self.check_overdue()

# Example data dictionaries
user_data = {
    "id":1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "password": "securepassword",
    "role": "Member"
}

book_data = {
    "id":1,
    "title": "A Great Book",
    "genre": "Fiction",
    "pages": 300,
    "total_copies": 5,
    "copies_available": 5
}

author_data = {
    "pen_name": "Jane Smith",
    "email": "jane.smith@example.com"
}

loan_data = {
    "borrower_id": 1,  # Assuming an existing user with id 1
    "borrowed_book_id": 1,  # Assuming an existing book with id 1
}

# Create instances using data dictionaries
user = User(**user_data)
book = Book(**book_data)
author = Author(**author_data)
loan = Loan(**loan_data)

# Output the instances to see the results
print(user)
print()
print(book)
print()
print(author)
print()
print(loan)


print()
print()
book1 = Book(title="A Great Book", genre="Fiction", pages=300, total_copies=5, copies_available=5)
book2 = Book(title="Another Book", genre="Non-Fiction", pages=200, total_copies=3, copies_available=2)

author = Author(pen_name="Jane Smith", email="jane.smith@example.com")

# Establish relationships
author.books.extend([book1, book2])

# Output bibliography
print(author.bibliography)