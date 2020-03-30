from pygraphdb.helpers import *
from pygraphdb.graph_base import GraphBase
from pygraphdb.plain_sql import PlainSQL


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
