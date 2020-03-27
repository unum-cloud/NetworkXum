from enum import Enum
import sqlite3

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy import or_, and_

from adapters.base import GraphBase
from helpers.shared import *

BaseEntitySQL = declarative_base()


class EdgeSQL(BaseEntitySQL):
    __tablename__ = 'edges'
    _id = Column(Integer, primary_key=True)
    v_from = Column(Integer, index=True)
    v_to = Column(Integer, index=True)
    weight = Column(Float)
    # directed = Column(Boolean)
    # attribute = Column(String)

    def __init__(self, v_from, v_to, weight=1, attribute='', directed=True):
        super().__init__()
        self._id = None
        self.v_from = v_from
        self.v_to = v_to
        self.weight = weight
        # self.directed = directed
        # self.attribute = attribute

    def __repr__(self):
        return f'<EdgeSQL(_id={self._id}, v_from={self.v_from}, v_to={self.v_to}, weight={self.weight})>'

    def __getitem__(self, key):
        if key == '_id':
            return self._id
        elif key == 'v_from':
            return self.v_from
        elif key == 'v_to':
            return self.v_to
        elif key == 'weight':
            return self.weight


class GraphSQL(GraphBase):
    '''
        A generic SQL-compatiable wrapper for Graph-shaped data.
        It's built on top of SQLAlchemy which supports following engines: 
        *   SQLite, 
        *   PostgreSQL, 
        *   MySQL, 
        *   Oracle, 
        *   MS-SQL, 
        *   Firebird, 
        *   Sybase. 
        Other dialects are published as external projects.
        This wrapper does not only emit the query results, 
        but can export the serialized quaery itself to be used 
        with other SQL-compatible systems.
        Docs: https://docs.python.org/3/library/sqlite3.html

        Queries can be exported without execution with `str(query)`, 
        but if you want to compile them for a specific dialect use following snippet:
        >>> str(query.statement.compile(dialect=postgresql.dialect()))
        Source: http://nicolascadou.com/blog/2014/01/printing-actual-sqlalchemy-queries/
    '''

    def __init__(self, url='sqlite:///:memory:'):
        super().__init__()
        self.engine = sa.create_engine(url)
        self.table_name = EdgeSQL.__tablename__
        self.session_maker = sessionmaker(bind=self.engine)
        self.session = self.session_maker()
        BaseEntitySQL.metadata.create_all(self.engine)

    def insert(self, e: EdgeSQL, check_uniqness=True) -> bool:
        if check_uniqness:
            if '_id' not in e:
                # First make sure we don't have such row.
                pass

        if not isinstance(e, EdgeSQL):
            e = EdgeSQL(e['v_from'], e['v_to'], e['weight'])
        self.session.add(e)
        self.session.commit()

    def delete(self, e: EdgeSQL) -> bool:
        if e['_id'] is not None:
            EdgeSQL.query.filter_by(id=e['_id']).delete()
        else:
            EdgeSQL.query.filter_by(
                v_from=e['v_from'],
                v_to=e['v_to'],
            ).delete()

    def find_directed(self, v_from, v_to) -> Optional[EdgeSQL]:
        return self.session.query(EdgeSQL).filter(and_(
            EdgeSQL.v_from == v_from,
            EdgeSQL.v_to == v_to,
        )).first()

    def find_undirected(self, v1, v2) -> Optional[EdgeSQL]:
        return self.session.query(EdgeSQL).filter(or_(
            and_(
                EdgeSQL.v_from == v1,
                EdgeSQL.v_to == v2,
            ),
            and_(
                EdgeSQL.v_from == v2,
                EdgeSQL.v_to == v1,
            )
        )).all()

    def all_vertexes(self) -> Set[int]:
        all_froms = self.session.query(EdgeSQL.v_from).distinct().all()

        all_tos = self.session.query(EdgeSQL.v_to).distinct().all()
        return set(all_froms).union(all_tos)

    def count_vertexes(self) -> int:
        return len(self.all_vertexes())

    def count_edges(self) -> int:
        return self.session.query(EdgeSQL).count()

    # Relatives

    def edges_from(self, v: int) -> List[EdgeSQL]:
        return self.session.query(EdgeSQL).filter_by(v_from=v).all()

    def edges_to(self, v: int) -> List[EdgeSQL]:
        return self.session.query(EdgeSQL).filter_by(v_to=v).all()

    def edges_related(self, v: int) -> List[EdgeSQL]:
        return self.session.query(EdgeSQL).filter(or_(
            EdgeSQL.v_from == v,
            EdgeSQL.v_to == v,
        )).all()

    def vertexes_related(self, v: int) -> Set[int]:
        # This is hard in SQL, so we just export the
        # edges and perform the rest in Python.
        result = set()
        for e in self.edges_related(v):
            result.add(e.v_from)
            result.add(e.v_to)
        result.remove(v)
        return result

    # Wider range of neighbours

    def vertexes_related_to_group(self, vs) -> Set[int]:
        edges = self.session.query(EdgeSQL).filter(or_(
            EdgeSQL.v_from.in_(vs),
            EdgeSQL.v_to.in_(vs),
        )).all()
        result = set()
        for e in edges:
            if (e.v_from not in vs):
                result.add(e.v_from)
            elif (e.v_to not in vs):
                result.add(e.v_to)
        return result

    # Metadata

    def count_related(self, v: int) -> (int, float):
        return self.session.query(
            func.count(EdgeSQL.weight).label("count"),
            func.sum(EdgeSQL.weight).label("sum"),
        ).filter(or_(
            EdgeSQL.v_from == v,
            EdgeSQL.v_to == v,
        )).first()

    def count_followers(self, v: int) -> (int, float):
        return self.session.query(
            func.count(EdgeSQL.weight).label("count"),
            func.sum(EdgeSQL.weight).label("sum"),
        ).filter_by(v_to=v).first()

    def count_following(self, v: int) -> (int, float):
        return self.session.query(
            func.count(EdgeSQL.weight).label("count"),
            func.sum(EdgeSQL.weight).label("sum"),
        ).filter_by(v_from=v).first()
