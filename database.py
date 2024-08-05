from sqlmodel import create_engine, SQLModel, Session
import os
from dotenv import load_dotenv

load_dotenv()

# Get the database URL from the environment variable
SQLALCHEMY_DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:secret@localhost:5432/library")

engine = create_engine(SQLALCHEMY_DB_URL)

# Create the database tables
def init_db():
    SQLModel.metadata.create_all(bind=engine)

def get_db():
    # Use a context manager for the session
    with Session(engine) as db:
        yield db
