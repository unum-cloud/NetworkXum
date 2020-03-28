from typing import List, Optional, Dict, Generator, Set, Tuple, Sequence

from neo4j import GraphDatabase

from pygraphdb.edge import Edge
from pygraphdb.graph_base import GraphBase


class Neo4j(GraphBase):
    """
        Uses Bolt API for Neo4j graph database.
    """

    def __init__(self, url='bolt://0.0.0.0:7687', enterprise_edition=False):
        super().__init__()
        self.driver = GraphDatabase.driver(url, encrypted=False)
        self.session = self.driver.session()
        self.delete_all()
        self.create_index_nodes()
        # Edge indexes are only availiable to Enterprise Edition customers.
        # https://neo4j.com/docs/cypher-manual/current/administration/constraints/#administration-constraints-syntax
        if enterprise_edition:
            self.create_index_edges()

    def create_index_nodes(self):
        task = '''
        CREATE CONSTRAINT unique_nodes
        ON (v:Vertex)
        ASSERT (v._id) IS UNIQUE
        '''
        return self.session.run(task)

    def create_index_edges(self):
        task = '''
        CREATE CONSTRAINT unique_edges
        ON ()-[e:]-()
        ASSERT (e._id) IS UNIQUE
        '''
        return self.session.run(task)

    # def __del__(self):
    #     self.driver.close()
    #     super().__del__()

    # Relatives

    def find_directed(self, v_from: int, v_to: int) -> Optional[object]:
        pattern = '''
        MATCH (a:Vertex {_id: %d})-[e:Edge]->(b:Vertex {_id: %d})
        RETURN e._id, e.weight, a._id, b._id
        '''
        task = (pattern % (v_from, v_to))
        return self.session.run(task)

    def find_undirected(self, v1: int, v2: int) -> Optional[object]:
        pattern = '''
        MATCH (a:Vertex {_id: %d})-[e:Edge]-(b:Vertex {_id: %d})
        RETURN a, e, b
        '''
        task = (pattern % (v1, v2))
        return self.session.run(task)

    def edges_from(self, v: int) -> List[object]:
        pattern = '''
        MATCH (a:Vertex {_id: %d})-[e:Edge]->(b:Vertex)
        RETURN a, e, b
        '''
        task = (pattern % (v))
        return self.session.run(task)

    def edges_to(self, v: int) -> List[object]:
        pattern = '''
        MATCH (a:Vertex)-[e:Edge]->(b:Vertex {_id: %d})
        RETURN a, e, b
        '''
        task = (pattern % (v))
        return self.session.run(task)

    def edges_related(self, v: int) -> List[object]:
        pattern = '''
        MATCH (a:Vertex {_id: %d})-[e:Edge]-(b:Vertex)
        RETURN a, e, b
        '''
        task = (pattern % (v))
        return self.session.run(task)

    # Wider range of neighbours

    def vertexes_related_to_group(self, vs: Sequence[int]) -> Set[int]:
        pass

    # Metadata

    def count_vertexes(self) -> int:
        pass

    def count_edges(self) -> int:
        pass

    def count_related(self, v: int) -> (int, float):
        pass

    def count_followers(self, v: int) -> (int, float):
        pass

    def count_following(self, v: int) -> (int, float):
        pass

    # Modifications

    def insert(self, e: Edge) -> bool:
        pattern = '''
        MERGE (v1:Vertex {_id: %d})
        MERGE (v2:Vertex {_id: %d})
        MERGE (v1)-[e:Edge {_id: %d, weight: %d}]->(v2)
        '''
        task = (pattern % (e['v_from'], e['v_to'], e['_id'], e['weight']))
        return self.session.run(task)

    def delete(self, e: object) -> bool:
        pass

    def delete_all(self):
        try:
            self.session.run('DROP CONSTRAINT unique_nodes;')
        except:
            pass
        self.session.run('MATCH (v) DETACH DELETE v;')


wrap = Neo4j()
print(wrap.insert(Edge(1, 3, 30)).keys())
print(wrap.insert(Edge(1, 4, 40)).keys())
print(wrap.insert(Edge(1, 5, 50)).keys())
print(wrap.insert(Edge(1, 6, 60)).keys())
print(list(wrap.find_directed(1, 3).records()))
