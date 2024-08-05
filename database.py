from sqlmodel import create_engine, SQLModel, Session
import os
from dotenv import load_dotenv

load_dotenv()

# Get the database URL from the environment variable
SQLALCHEMY_DB_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DB_URL, connect_args={"check_same_thread": False})

# Create the database tables
def init_db():
    SQLModel.metadata.create_all(bind=engine)

def get_db():
    db = Session(engine)
    try:
        yield db  # Use a generator for context management
    finally:
        db.close()
