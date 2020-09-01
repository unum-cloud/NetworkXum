from abc import ABC, abstractmethod
from contextlib import contextmanager

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, BigInteger, Text, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy import or_, and_
from sqlalchemy_utils import create_database, database_exists
from sqlalchemy import text
from sqlalchemy import Index, Table

from PyWrappedDocs.BaseAPI import BaseAPI
from PyWrappedHelpers.Algorithms import *

DeclarativeDocsSQL = declarative_base()


class TextSQL(DeclarativeDocsSQL):
    __tablename__ = 'table_nodes'
    _id = Column(BigInteger, primary_key=True)
    content = Column(Text)
    content_index = Index('content_index', TextSQL.content, unique=False)

    def __init__(self, *args, **kwargs):
        DeclarativeDocsSQL.__init__(self)


class BaseSQL(BaseAPI):
    """
        A generic SQL-compatiable wrapper for Textual data.
        It's built on top of SQLAlchemy which supports following engines:
        *   SQLite,
        *   PostgreSQL,
        *   MySQL,
        *   Oracle,
        *   MS-SQL,
        *   Firebird,
        *   Sybase.
    """
    __is_concurrent__ = True
    __in_memory__ = False

    # --------------------------------
    # region: Initialization and Metadata.
    # --------------------------------

    def __init__(self, url='sqlite:///:memory:', **kwargs):
        BaseAPI.__init__(self, **kwargs)
        # https://stackoverflow.com/a/51184173
        if not database_exists(url):
            create_database(url)
        self.engine = sa.create_engine(url)
        DeclarativeDocsSQL.metadata.create_all(self.engine)
        self.session_maker = sessionmaker(bind=self.engine)

    @contextmanager
    def get_session(self):
        session = self.session_maker()
        session.expire_on_commit = False
        try:
            yield session
            session.commit()
        except Exception as doc:
            print(doc)
            session.rollback()
            raise doc
        finally:
            session.close()

    def count_docs(self) -> int:
        result = 0
        with self.get_session() as s:
            result = s.query(TextSQL).count()
        return result

    # endregion

    # --------------------------------
    # region: Adding and removing documents.
    # --------------------------------

    def upsert_doc(self, doc: TextSQL) -> bool:
        result = False
        with self.get_session() as s:
            s.merge(doc)
            result = True
        return result

    def remove_doc(self, doc: TextSQL) -> bool:
        result = False
        with self.get_session() as s:
            s.query(TextSQL).filter_by(
                _id=doc._id
            ).delete()
            result = True
        return result

    def upsert_docs(self, docs: List[Edge]) -> int:
        result = 0
        with self.get_session() as s:
            docs = list(map(s.merge, docs))
            result = len(docs)
        return result

    def remove_all(self) -> int:
        result = 0
        with self.get_session() as s:
            result += s.query(TextSQL).delete()
        return result

    # endregion

    # --------------------------------
    # region: Search Queries.
    # --------------------------------

    @abstractmethod
    def find_with_substring(self, field: str, query: str) -> Sequence[Text]:
        pass

    @abstractmethod
    def find_with_regex(self, field: str, query: str) -> Sequence[Text]:
        pass

    def find_with_id(self, identifier: str) -> object:
        pass

    # endregion
