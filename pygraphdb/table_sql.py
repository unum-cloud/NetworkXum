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

from pygraphdb.base_graph import GraphBase
from pygraphdb.base_edge import Edge
from pygraphdb.helpers import *

BaseEntitySQL = declarative_base()


class NodeSQL(BaseEntitySQL):
    __tablename__ = 'table_nodes'
    _id = Column(BigInteger, primary_key=True)
    attributes_json = Column(Text)

    def __init__(self, *args, **kwargs):
        BaseEntitySQL.__init__(self)


class EdgeSQL(BaseEntitySQL, Edge):
    __tablename__ = 'table_edges'
    _id = Column(BigInteger, primary_key=True)
    v_from = Column(BigInteger, index=True)
    v_to = Column(BigInteger, index=True)
    weight = Column(Float)
    attributes_json = Column(Text)

    def __init__(self, *args, **kwargs):
        BaseEntitySQL.__init__(self)
        Edge.__init__(self, *args, **kwargs)


class EdgeNew(BaseEntitySQL, Edge):
    __tablename__ = 'new_edges'
    # TODO: Consider using different Integer types in different SQL DBs.
    # https://stackoverflow.com/a/60840921/2766161
    _id = Column(BigInteger, primary_key=True)
    v_from = Column(BigInteger, index=False)
    v_to = Column(BigInteger, index=False)
    weight = Column(Float)
    attributes_json = Column(Text)

    def __init__(self, *args, **kwargs):
        BaseEntitySQL.__init__(self)
        Edge.__init__(self, *args, **kwargs)


class PlainSQL(GraphBase):
    """
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

        CAUTION:
        Implementations of analytical queries are suboptimal, 
        as implementing them in SQL dialects is troublesome and 
        often results in excessive memory consumption, 
        when temporary tables are created.

        CAUTION:
        Queries can be exported without execution with `str(query)`, 
        but if you want to compile them for a specific dialect use following snippet:
        >>> str(query.statement.compile(dialect=postgresql.dialect()))
        Source: http://nicolascadou.com/blog/2014/01/printing-actual-sqlalchemy-queries/
    """
    __is_concurrent__ = True
    __max_batch_size__ = 5000
    __edge_type__ = EdgeSQL

    def __init__(self, url='sqlite:///:memory:', **kwargs):
        GraphBase.__init__(self, **kwargs)
        # https://stackoverflow.com/a/51184173
        if not database_exists(url):
            create_database(url)
        self.engine = sa.create_engine(url)
        BaseEntitySQL.metadata.create_all(self.engine)
        self.session_maker = sessionmaker(bind=self.engine)

    @contextmanager
    def get_session(self):
        session = self.session_maker()
        try:
            yield session
            session.commit()
        except Exception as e:
            print(e)
            session.rollback()
            raise e
        finally:
            session.close()

    # Relatives

    def find_edge(self, v_from: int, v_to: int) -> Optional[EdgeSQL]:
        with self.get_session() as s:
            return s.query(EdgeSQL).filter(and_(
                EdgeSQL.v_from == v_from,
                EdgeSQL.v_to == v_to,
            )).first()
        return None

    def find_edge_or_inv(self, v1: int, v2: int) -> Optional[EdgeSQL]:
        with self.get_session() as s:
            return s.query(EdgeSQL).filter(or_(
                and_(
                    EdgeSQL.v_from == v1,
                    EdgeSQL.v_to == v2,
                ),
                and_(
                    EdgeSQL.v_from == v2,
                    EdgeSQL.v_to == v1,
                )
            )).all()
        return None

    def edges_from(self, v: int) -> List[EdgeSQL]:
        with self.get_session() as s:
            return s.query(EdgeSQL).filter_by(v_from=v).all()
        return []

    def edges_to(self, v: int) -> List[EdgeSQL]:
        with self.get_session() as s:
            return s.query(EdgeSQL).filter_by(v_to=v).all()
        return []

    def edges_related(self, v: int) -> List[EdgeSQL]:
        with self.get_session() as s:
            return s.query(EdgeSQL).filter(or_(
                EdgeSQL.v_from == v,
                EdgeSQL.v_to == v,
            )).all()
        return []

    def all_vertexes(self) -> Set[int]:
        with self.get_session() as s:
            all_froms = s.query(EdgeSQL.v_from).distinct().all()
            all_tos = s.query(EdgeSQL.v_to).distinct().all()
            return set(all_froms).union(all_tos)
        return set()

    # Wider range of neighbors

    def nodes_related_to_group(self, vs: Sequence[int]) -> Set[int]:
        with self.get_session() as s:
            edges = s.query(EdgeSQL).filter(or_(
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
        return set()

    # Metadata

    def count_nodes(self) -> int:
        return len(self.all_vertexes())

    def count_edges(self) -> int:
        with self.get_session() as s:
            return s.query(EdgeSQL).count()
        return 0

    def count_related(self, v: int) -> (int, float):
        with self.get_session() as s:
            return s.query(
                func.count(EdgeSQL.weight).label("count"),
                func.sum(EdgeSQL.weight).label("sum"),
            ).filter(or_(
                EdgeSQL.v_from == v,
                EdgeSQL.v_to == v,
            )).first()
        return (0, 0)

    def count_followers(self, v: int) -> (int, float):
        with self.get_session() as s:
            return s.query(
                func.count(EdgeSQL.weight).label("count"),
                func.sum(EdgeSQL.weight).label("sum"),
            ).filter_by(v_to=v).first()
        return (0, 0)

    def count_following(self, v: int) -> (int, float):
        with self.get_session() as s:
            return s.query(
                func.count(EdgeSQL.weight).label("count"),
                func.sum(EdgeSQL.weight).label("sum"),
            ).filter_by(v_from=v).first()
        return (0, 0)

    def biggest_edge_id(self) -> int:
        with self.get_session() as s:
            biggest = s.query(
                func.max(EdgeSQL._id).label("max"),
            ).first()
            if biggest[0] is None:
                return 0
            return biggest[0]
        return 0

    # Modifications

    def upsert_edge(self, e: EdgeSQL) -> bool:
        with self.get_session() as s:
            e = self.validate_edge(e)
            if e is None:
                return False
            s.merge(e)
            return True
        return False

    def remove_edge(self, e: EdgeSQL) -> bool:
        with self.get_session() as s:
            if '_id' in e:
                s.query(EdgeSQL).filter_by(
                    _id=e['_id']
                ).delete()
            else:
                s.query(EdgeSQL).filter_by(
                    v_from=e['v_from'],
                    v_to=e['v_to'],
                ).delete()
            return True
        return False

    def upsert_edges(self, es: List[Edge]) -> int:
        with self.get_session() as s:
            es = map_compact(self.validate_edge, es)
            map(s.merge, es)
            return len(es)
        return 0

    def remove_node(self, v: int) -> int:
        with self.get_session() as s:
            count = s.query(EdgeSQL).filter(or_(
                EdgeSQL.v_from == v,
                EdgeSQL.v_to == v,
            )).delete()
            return count
        return 0

    def remove_all(self) -> int:
        with self.get_session() as s:
            count = 0
            count += s.query(EdgeSQL).delete()
            count += s.query(EdgeNew).delete()
            return count
        return 0

    def insert_adjacency_list(self, path: str) -> int:
        with self.get_session() as s:
            current_id = self.biggest_edge_id() + 1
            # Build the new table.
            chunk_len = type(self).__max_batch_size__
            for es_raw in chunks(yield_edges_from(path), chunk_len):
                for i, e in enumerate(es_raw):
                    e['_id'] = current_id
                    es_raw[i] = e
                    current_id += 1
                es = map(EdgeNew, es_raw)
                es = map_compact(self.validate_edge, es_raw)
                s.bulk_save_objects(
                    es,
                    return_defaults=False,
                    update_changed_only=True,
                    preserve_order=False,
                )
            # Import the new data.
            cnt = self.count_edges()
            self.insert_table(EdgeNew.__tablename__)
            self.flush_temporary_table()
            return self.count_edges() - cnt
        return 0

    def insert_table(self, source_name: str):
        with self.get_session() as s:
            migration = text(f'''
                INSERT INTO {EdgeSQL.__tablename__}
                SELECT * FROM {source_name};
            ''')
            s.execute(migration)
        return 0

    def upsert_adjacency_list(self, path: str) -> int:
        """
            Direct injections (even in batches) have huge performance impact.
            We are not only conflicting with other operations in same DB, 
            but also constantly rewriting indexes after every new batch insert.
            Instead we create a an additional unindexed table, fill it and
            then merge into the main one.
        """
        with self.get_session() as s:
            # Build the new table.
            chunk_len = type(self).__max_batch_size__
            for es in chunks(yield_edges_from(path), chunk_len):
                es = map_compact(self.validate_edge, es)
                self.map(s.merge, es)
            # Import the new data.
            cnt = self.count_edges()
            self.upsert_table(EdgeNew.__tablename__)
            self.flush_temporary_table()
            return self.count_edges() - cnt
        return 0

    @abstractmethod
    def upsert_table(self, source_name: str):
        with self.get_session() as s:
            migration = text(f'''
                REPLACE INTO {EdgeSQL.__tablename__}
                SELECT * FROM {source_name};
            ''')
            # Performing an `INSERT` and then a `DELETE` might lead to integrity issues,
            # so perhaps a way to get around it, and to perform everything neatly in
            # a single statement, is to take advantage of the `[deleted]` temporary table.
            # migration = text(f'''
            # DELETE {EdgeNew.__tablename__};
            # OUTPUT DELETED.*
            # INTO {EdgeSQL.__tablename__} (_id, v_from, v_to, weight, attributes_json)
            # ''')
            # But this syntax isn't globally supported.
            s.execute(migration)

    def insert_bulk_deduplicated(self, es: List[EdgeNew]):
        # Some low quality datasets contain duplicates and
        # if we have ID collisions, the operation will fail.
        # https://docs.sqlalchemy.org/en/13/orm/session_api.html#sqlalchemy.orm.session.Session.bulk_save_objects
        with self.get_session() as s:
            s.bulk_save_objects(
                es,
                return_defaults=False,
                update_changed_only=True,
                preserve_order=False,
            )

    def flush_temporary_table(self):
        with self.get_session() as s:
            s.execute(text(f'DELETE FROM {EdgeNew.__tablename__};'))

    def validate_edge(self, e) -> BaseEntitySQL:
        if not isinstance(e, BaseEntitySQL):
            e = EdgeNew(v_from=e['v_from'], v_to=e['v_to'],
                        _id=e['_id'], weight=e['weight'])
        return super().validate_edge(e)
