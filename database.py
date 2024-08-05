
from sqlmodel import create_engine, SQLModel,Session

DATABASE_URL = "postgresql+psycopg2://myuser:mypassword@postgres:5432/mydatabase"
engine = create_engine(DATABASE_URL)

# Create the database tables
def init_db():
    SQLModel.metadata.create_all(bind=engine)

def get_db():
    # Use a context manager for the session
    with Session(engine) as db:
        yield db
