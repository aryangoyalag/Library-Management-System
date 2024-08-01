from sqlalchemy import Column, Integer, String, DATE, Table, ForeignKey, Boolean,func
from sqlalchemy.orm import relationship, event
from database import Base, SessionLocal
from datetime import datetime, timedelta

book_author_association = Table(
    'book_author_association',
    Base.metadata,
    Column('book_id', Integer, ForeignKey('books.id'), primary_key = True),
    Column('author_id', Integer, ForeignKey('authors.id'),primary_key = True)
)

class User(Base):
    __tablename__ = 'users'

    id = Column( Integer, primary_key = True)
    first_name = Column( String, nullable = False, index = True)
    last_name = Column( String, nullable = False, index = True)
    email = Column( String, unique = True, nullable = False)
    password = Column( String, nullable = False)
    role = Column( String, nullable = False, default = 'Member')

class Book(Base):
    __tablename__ = 'books'

    id = Column( Integer, primary_key = True)
    title = Column( String, nullable = False, index = True)
    genre = Column( String, nullable = True, index = True)
    pages = Column( Integer, nullable = True)
    total_copies = Column( Integer, nullable = False)
    copies_available = Column( Integer, nullable = True)
    copies_on_rent = Column( Integer, default = 0,nullable = False)
    next_available_on = Column(DATE, nullable = True)
    authors = relationship('Author',secondary = book_author_association,back_populates='books')

@event.listens_for(Book, 'before_insert')
def set_copies_available(mapper, connection, target):
    if target.copies_available is None:
        target.copies_available = target.total_copies

class Author(Base):
    __tablename__ = 'authors'

    id = Column( Integer, primary_key = True)
    pen_name = Column( String, nullable = False, index = True)
    email = Column( String, unique = True, nullable = False)
    books = relationship('Book',secondary = book_author_association, back_populates = 'authors')

    @property
    def bibliography(self):
        return [book.title for book in self.books]

class Loan(Base):
    __tablename__ = 'loans'

    id = Column( Integer, primary_key = True)
    borrower_id = Column( Integer, ForeignKey('users.id'), nullable = False)
    borrowed_book_id = Column( Integer, ForeignKey('books.id'), nullable = False)
    issue_date = Column( DATE, default = func.now(), nullable = False)
    due_date = Column( DATE, nullable = False)
    returned = Column( Boolean, default = False)
    overdue = Column( Boolean, default = False)
    loan_amount = Column( Integer, default = 50,nullable = False)
    fine = Column( Integer, default = 0)

    borrower = relationship('User')
    borrowed_book = relationship('Book')

    def __init__(self, borrower_id, borrowed_book_id):
        self.borrower_id = borrower_id
        self.borrowed_book_id = borrowed_book_id
        self.issue_date = datetime.utcnow().date()
        self.due_date = self.issue_date + timedelta(days=15)
    
    def check_overdue(self):
        if not self.returned and datetime.utcnow().date() > self.due_date:
            self.overdue = True
            days_overdue = (datetime.utcnow().date() - self.due_date).days
            self.fine = days_overdue * 10
        else:
            self.overdue = False
            self.fine = 0
    
    def return_book(self):
        self.returned = True
        self.check_overdue()

@event.listens_for(Loan, 'before_insert')
def update_book_on_loan(mapper, connection, target):
    book_id = target.borrowed_book_id
    session = SessionLocal()
    
    try:
        book = session.query(Book).filter(Book.id == book_id).one()
        
        book.copies_on_rent += 1
        book.copies_available -= 1
        if book.copies_available == 0:
            next_due_date = session.query(Loan.due_date).filter(Loan.borrowed_book_id == book_id, Loan.returned == False).order_by(Loan.due_date).first()
            book.next_available_on = next_due_date[0] if next_due_date else None

        session.commit()
    finally:
        session.close()

@event.listens_for(Loan, 'before_update')
def update_book_on_return(mapper, connection, target):
    if target.returned:
        book_id = target.borrowed_book_id
        session = SessionLocal()
        
        try:
            book = session.query(Book).filter(Book.id == book_id).one()
            
            book.copies_on_rent -= 1
            book.copies_available += 1
            if book.copies_available > 0:
                book.next_available_on = datetime.utcnow().date()
            else:
                next_due_date = session.query(Loan.due_date).filter(Loan.borrowed_book_id == book_id, Loan.returned == False).order_by(Loan.due_date).first()
                book.next_available_on = next_due_date[0] if next_due_date else None

            session.commit()
        finally:
            session.close()

@event.listens_for(Loan,'load')
@event.listens_for(Loan,'refresh')
def recieve_load(target,context):
    target.check_overdue()

@event.listens_for(Loan, 'before_insert')
@event.listens_for(Loan, 'before_update')
def recieve_before_insert(mapper, connection, target):
    target.check_overdue()