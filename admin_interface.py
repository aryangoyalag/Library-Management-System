from starlette_admin.contrib.sqla import Admin, ModelView
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
import models

# Create SQLAlchemy engine and session
DATABASE_URL = "postgresql://postgres:secret@localhost:5432/library"  # Adjust to your DB URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define views for your models
class BookModelView(ModelView):
    columns = ['id', 'title', 'genre', 'pages', 'total_copies', 'copies_available', 'copies_on_rent', 'next_available_on']

class AuthorModelView(ModelView):
    columns = ['id', 'pen_name', 'email', 'books']

class UserModelView(ModelView):
    columns = ['id', 'first_name', 'last_name', 'email', 'role', 'loans']

class LoanModelView(ModelView):
    columns = ['id', 'borrower_id', 'borrowed_book_id', 'issue_date', 'due_date', 'returned', 'overdue', 'loan_amount', 'fine']

class NotificationModelView(ModelView):
    columns = ['id', 'user_id', 'message', 'is_read', 'created_at']

# Initialize the Starlette app
admin_app = Starlette()

# Configure the admin interface
admin = Admin(
    sessionmaker=SessionLocal,
    models=[models.Book, models.Author, models.User, models.Loan, models.Notification],
    views={
        models.Book: BookModelView,
        models.Author: AuthorModelView,
        models.User: UserModelView,
        models.Loan: LoanModelView,
        models.Notification: NotificationModelView,
    }
)

# Mount the admin interface on the Starlette app
admin_app.mount("/admin", admin, name="admin")

# Serve static files for the admin interface
admin_app.mount("/static", StaticFiles(directory="static"), name="static")
