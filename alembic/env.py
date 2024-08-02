from __future__ import annotations
import sys
import os
from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import sessionmaker
from alembic import context
from sqlmodel import SQLModel

# Add your project directory to the sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import your models here
from models import Book, Author, User, Loan  # Update the import path

# Configure Alembic
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the target metadata for Alembic
target_metadata = SQLModel.metadata

# Define the database URL
def get_engine():
    return create_engine(config.get_main_option("sqlalchemy.url"))

# Run migrations
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
