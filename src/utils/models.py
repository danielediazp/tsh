from datetime import datetime, timezone
from enum import StrEnum, auto

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import as_declarative, declared_attr, relationship


class TaskStatus(StrEnum):
    ACTIVE = auto()
    INACTIVE = auto()


@as_declarative()
class Base:
    """class to define a Base SQL Alchemy ORM.

    This class Defines a Base object that should be instantiated in all the database tables throughout
    this project.

    Defines:
        __tablename__ : Uses the class name all lower case for the table name
        __repr__: Represents the class as a dictionary
    """

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def __repr__(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return f"{self.__class__.__name__}({data!r})"


class Task(Base):
    """Represent a unit of work to be completed.

    This ORM model maps to the `task` table in the SQLite database and
    encapsulates all metadata for a single task instance.

    Attributes:
        id (int): Auto incrementing primary key.
        title (str): Brief, human readable title of the task. Must not be null.
        description (str | None): Optional, longer description or notes.
        creation_at (Datetime): UTC timestamp when this task was created.
        completed_at (Datetime): UTC timestamp when this task was marked as completed.
        is_deleted (boolean | Optional): A boolean representing if the task has been deleted. Defaults to False.
        status (str): The current status of the test. Defaults to active.
        history (History): Maps to the `History` ORM model for the history of the `Task`.
    """

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(
        DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None), index=True
    )
    completed_at = Column(DateTime, index=True)
    is_deleted = Column(Boolean, default=False)
    status = Column(String, default=TaskStatus.ACTIVE, index=True)

    history = relationship(
        "History", back_populates="task", lazy="joined", uselist=True
    )


class History(Base):
    """Represents the edit history of a task.

    This ORM model maps to the `history` table in the SQLite database and
    encapsulates all metadata related to tasks edits.

    Attributes:
    id (int): Auto incrementing primary key.
    task_id (int): Foreign key that maps to the completed task in the `task` table.
    old_description (str): Represents the old description of the task.
    new_description (str): Represents the new description of the task.
    timestamp (Datetime): Represents the timestamp at which the edit happened.
    """

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("task.id", ondelete="CASCADE"), nullable=False)
    old_description = Column(String, nullable=False)
    new_description = Column(String, nullable=False)
    timestamp = Column(
        DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None)
    )

    task = relationship("Task", back_populates="history", lazy="joined")
