from neo4j import GraphDatabase

from helpers.shared import *
from pygraphdb.graph_base import GraphBase
from pygraphdb.plain_sql import PlainSQL


class Neo4j(GraphBase):
    """
        Uses Bolt API for Neo4j graph database.
    """

    def __init__(self, url='bolt://localhost:7687', collection_name=''):
        super().__init__()
        self.driver = GraphDatabase.driver(url, auth=("neo4j", "password"))
        pass


class Cayley(GraphBase):
    """
        Actual graph database written in Go with usable Python bindings.
        It was tailoerd for RDFa triplets, but can be repurposed for
        classical graphs.

        https://github.com/ziyasal/pyley
        https://github.com/cayleygraph/cayley
        https://github.com/cayleygraph/cayley/blob/master/docs/gizmoapi.md
    """
    pass


class PostgreSQL(PlainSQL):
    """
        Extends PlainSQL functionality with optimized operations:
        *   Bulk imports and exports via:
            https://github.com/jmcarp/sqlalchemy-postgres-copy
        *   Async operations through less mature ORM: Gino (only PostgreSQL).
            https://github.com/python-gino/gino
        *   Allows natively quering JSON subproperties via:
            https://sqlalchemy-utils.readthedocs.io/en/latest/data_types.html#module-sqlalchemy_utils.types.json        

    """
    pass


class BlazingSQL(PlainSQL):
    """
        Redirects SQL queries generated for actual DBs
        to GPU-accelerated single-file analytics enginge.
        It's built on top of Rapids.ai and only work on NVidia GPUs.

        https://blazingsql.com/
    """
    pass


class NestedRocksDB(GraphBase):
    # Each key is: "from_id:to_id"
    # Each value is: "weight"
    # OR:
    # Each key is: "node_id"
    # Each value is: { "relations_from": [], "relations_to": [] }
    pass
