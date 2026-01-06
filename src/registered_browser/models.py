"""Module for defining registered browser data models.

Classes:
    - RegisteredBrowser: SQLAlchemy model for the 'registered_browsers' table in
        the database.

"""

from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base
from src.registered_browser.constants import IDENTIFIER


class RegisteredBrowser(Base):
    """SQLAlchemy model for registered browser data.

    Attributes:
        id (int): Browser's unique identifier.
        browser_uuid (str): Browser's unique UUID.
        browser_name (str): Browser's friendly name.

    """

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    browser_uuid: Mapped[str] = mapped_column(unique=True, nullable=False)
    browser_name: Mapped[str] = mapped_column(nullable=False)

    __tablename__ = IDENTIFIER
