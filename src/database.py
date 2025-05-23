"""Module establishing and providing access to a database connection."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy import Table, create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    declarative_base,
    sessionmaker,
)

Base: DeclarativeBase = declarative_base()

SQL_ALCHEMY_DATABASE_URL = "sqlite:///tep.sqlite"


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


engine = create_engine(SQL_ALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Get a database session.

    Yields:
        Session: A database session.

    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DatabaseSession = Annotated[SessionLocal, Depends(get_db)]


def cleanup_tables(db: Session):
    """Cleans up all existing tables.

    Args:
        db (Session): Database session for cleanup.

    """
    tables = reversed(Base.metadata.sorted_tables)
    for table in tables:
        delete_all_table_data(table, db)
        reset_primary_key(table, db)


def delete_all_table_data(table: Table, db: Session):
    """Delete all data from the given table.

    Args:
        table (Table): The table to delete data from.
        db (Session): Database session for cleanup.

    """
    db.query(table).delete()
    db.commit()


def reset_primary_key(table: Table, db: Session):
    """Reset the primary keys for the given tablename.

    Args:
        table (Table): The table to reset primary key for.
        db (Session): Database session for cleanup.

    """
    reset_sequence = text(
        f"ALTER SEQUENCE {table.name}_id_seq RESTART WITH 1;"
    )
    db.execute(reset_sequence)
    db.commit()
