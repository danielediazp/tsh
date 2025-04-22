from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import as_declarative, declared_attr, relationship


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
        creation_datetime (datetime.datetime): UTC timestamp when this task was created.
        completed (CompletedTask): Maps to the `CompletedTask` ORM model when the task is marked as completed.
    """

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String)
    creation_datetime = Column(
        DateTime(timezone=False),
        default=datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False,
    )

    completed = relationship("CompletedTask", back_populates="task", lazy="joined")


class CompletedTask(Base):
    """Represents a unit of work that has been completed.

    This ORM model maps to the `completed` table in the SQLite database and
    encapsulates all metadata for completed tasks instances.

    Attributes:
        id (int): Auto incrementing primary key.
        completed_datetime (datetime.datetime): UTC timestamp of when the task was completed.
        task_id (int): Foreign key that maps to the completed task in the `task` table.
        task (Task): Maps to the `Task` ORM model for the task for the instance that was completed.
    """

    id = Column(Integer, primary_key=True, autoincrement=True)
    completed_datetime = Column(
        DateTime(timezone=False),
        default=datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False,
        index=True,
    )
    task_id = Column(Integer, ForeignKey("task.id", ondelete="CASCADE"), nullable=False)

    task = relationship("Task", back_populates="completed", lazy="joined")
