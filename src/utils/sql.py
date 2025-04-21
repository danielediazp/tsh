import logging
from typing import Any, Type, TypeVar

from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import sessionmaker, Session, joinedload
from contextlib import contextmanager

from .models import Base
from exceptions import ModelNotFoundError


LOGGER = logging.getLogger(__name__)
T = TypeVar("T", bound=Base)


class SqlManager:
    """
    Manages a SQLite database connection, schema creation, and session lifecycle.

    Methods:
        __init__
        get_session
        query
        insert
        update
        delete
    """

    def __init__(self, db_name: str, future: bool = True):
        """Initialize the SQL engine and session factory.

        Args:
            db_name (str): the file_path to the db.
            future (bool, optional): Whether to use SQLAlchemy 2.0-style engine semantics. Defaults to True.
        """
        self.engine: Engine = create_engine(db_name, future=future)

        # FKs are not enable by default in SQLite
        # Any Fks constrain will be ignore unless set
        @event.listens_for(self.engine, "connect")
        def _enable_fks(dbapi_conn, _):
            dbapi_conn.execute("PRAGMA foreign_keys=ON")

        self.session: sessionmaker[Session] = sessionmaker(
            bind=self.engine, future=True, expire_on_commit=False
        )
        self._create_table()

    def _create_table(self) -> None:
        """Creates all tables `IF NOT EXIST` define in `models.py`"""
        Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def get_session(self):
        """Provide a transactional scope around a series of operations.

        Yields:
            A SQLAlchemy Session that is committed on success and, rollback on exception, and always closed.
        """
        curr_session = self.session()
        try:
            yield curr_session
            curr_session.commit()
        except Exception:
            curr_session.rollback()
            raise
        finally:
            curr_session.close()

    def query(
        self,
        model: Type[T],
        single: bool = False,
        **params: Any,
    ) -> T | list[T] | None:
        """Query the database for one or more rows of the given model.

        Args:
            model: The SQLAlchemy ORM model class to query.
            single: If True, return at most one object (or None). If False, return a list.
            eager: A list of relationship attribute names to eagerly load.
            **params: Column value filters to apply.

        Returns:
            If single=True: a single instance of model or None if no match.
            If single=False: a list of matching instances (possibly empty).
        """
        with self.get_session() as s:
            q = s.query(model).filter_by(**params)
            return q.one_or_none() if single else q.all()

    def insert(self, objs: T | list[T]) -> T | list[T]:
        """Inserts objects in to the database.

        Args:
            objs (T | list[T]): A list or single model that implements `Base`.

        Returns:
            T | list[T]: the inserted objects with the defaults populated.
        """
        with self.get_session() as s:
            if isinstance(objs, list):
                s.add_all(objs)
            else:
                s.add(objs)
            s.flush()
            return objs

    def update(self, model: Type[T], ident: int, **updates: Any) -> T:
        """Updates a single row in the database by primary key.

        Args:
            model (Type[T]): The SQLAlchemy model class to update.
            ident (int): The primary key of the row.
            updates (Any): The fields to update.

        Returns:
            T: The updated instance

        Raises:
            ModelNotFoundError: If the object is not found
        """
        with self.get_session() as s:
            entry = s.get(model, ident)

            if entry is None:
                raise ModelNotFoundError(
                    f"model=[{model.__name__}] with ident=[{ident}] not found."
                )

            for field, value in updates.items():
                setattr(entry, field, value)

            s.flush()
            return entry

    def delete(self, model: Type[T], **params: Any) -> None:
        """Deletes one or more entries from the database.

        Args:
            model (Type[T]): _description_
            params (Any): The list of parameters to filter by
        """
        with self.get_session() as s:
            s.query(model).filter_by(**params).delete()
            s.flush()
