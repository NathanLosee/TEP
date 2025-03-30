"""Module for defining encounter data models.

Classes:
    - Job: SQLAlchemy model for the 'jobs' table in the database.

"""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from src.department.constants import IDENTIFIER as DEPARTMENT_IDENTIFIER
from src.job.constants import IDENTIFIER
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.department.models import Department
else:
    Department = "Department"


class Job(Base):
    """SQLAlchemy model for Job data.

    Attributes:
        id (int): Unique identifier of the jobs's data in the database.
        name (str): Name of the job.

    """

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    department_id: Mapped[int] = mapped_column(
        ForeignKey(DEPARTMENT_IDENTIFIER + ".id"),
        nullable=False,
    )
    department: Mapped[Department] = relationship(passive_deletes=True)

    __tablename__ = IDENTIFIER
