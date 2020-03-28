from typing import List, Optional, Dict, Generator, Set, Tuple, Sequence

from neo4j import GraphDatabase
from neo4j import BoltStatementResult

from pygraphdb.edge import Edge
from pygraphdb.graph_base import GraphBase


class Neo4j(GraphBase):
    """
        Uses Bolt API for Neo4j graph database.
        This is a suboptimal implementation, as we query nodes 
    """

    def __init__(self, url='bolt://0.0.0.0:7687', enterprise_edition=False):
        super().__init__()
        self.driver = GraphDatabase.driver(url, encrypted=False)
        self.session = self.driver.session()
        self.delete_all()
        self.create_index_nodes()
        if enterprise_edition:
            self.create_index_edges()

    def create_index_nodes(self):
        # Existing uniqness constraint means,
        # that we don't have to create a separate index.
        task = '''
        CREATE CONSTRAINT unique_nodes
        ON (v:Vertex)
        ASSERT (v._id) IS UNIQUE
        '''
        return self.session.run(task)

    def create_index_edges(self):
        # Edge uniqness constrains are only availiable to Enterprise Edition customers.
        # https://neo4j.com/docs/cypher-manual/current/administration/constraints/#administration-constraints-syntax
        task = '''
        CREATE CONSTRAINT unique_edges
        ON ()-[e:]-()
        ASSERT (e._id) IS UNIQUE
        '''
        # Indexes on relationships are not implemented yet.
        # https://stackoverflow.com/a/22444108
        # task = '''
        # CREATE INDEX ids_edges
        # FOR [e:Edge]
        # ON (e._id)
        # '''
        return self.session.run(task)

    # def __del__(self):
    #     self.driver.close()
    #     super().__del__()

    # Relatives

    def edge_directed(self, v_from: int, v_to: int) -> Optional[object]:
        pattern = '''
        MATCH (v_from:Vertex {_id: %d})-[e:Edge]->(v_to:Vertex {_id: %d})
        RETURN v_from._id, v_to._id, e.weight
        '''
        task = (pattern % (v_from, v_to))
        return self._records_to_edges(self.session.run(task))

    def edge_undirected(self, v1: int, v2: int) -> Optional[object]:
        pattern = '''
        MATCH (v_from:Vertex {_id: %d})-[e:Edge]-(v_to:Vertex {_id: %d})
        RETURN v_from._id, v_to._id, e.weight
        '''
        task = (pattern % (v1, v2))
        return self._records_to_edges(self.session.run(task))

    def edges_from(self, v: int) -> List[object]:
        pattern = '''
        MATCH (v_from:Vertex {_id: %d})-[e:Edge]->(v_to:Vertex)
        RETURN v_from._id, v_to._id, e.weight
        '''
        task = (pattern % (v))
        return self._records_to_edges(self.session.run(task))

    def edges_to(self, v: int) -> List[object]:
        pattern = '''
        MATCH (v_from:Vertex)-[e:Edge]->(v_to:Vertex {_id: %d})
        RETURN v_from._id, v_to._id, e.weight
        '''
        task = (pattern % (v))
        return self._records_to_edges(self.session.run(task))

    def edges_related(self, v: int) -> List[object]:
        pattern = '''
        MATCH (v_from:Vertex {_id: %d})-[e:Edge]-(v_to:Vertex)
        RETURN v_from._id, v_to._id, e.weight
        '''
        task = (pattern % (v))
        return self._records_to_edges(self.session.run(task))

    # Wider range of neighbours

    def edges_related_to_group(self, vs: Sequence[int]) -> List[Edge]:
        pattern = '''
        MATCH (v_from:Vertex)-[e:Edge]-(v_to:Vertex)
        WHERE (v_from._id IN [%s]) AND NOT (v_to._id IN [%s])
        RETURN v_from._id, v_to._id, e.weight
        '''
        group_members = ','.join([str(v) for v in vs])
        task = (pattern % (group_members, group_members))
        return self._records_to_edges(self.session.run(task))

    def vertexes_related_to_group(self, vs: Sequence[int]) -> Set[int]:
        pattern = '''
        MATCH (v_from:Vertex)-[e:Edge]-(v_to:Vertex)
        WHERE (v_from._id IN [%s]) AND NOT (v_to._id IN [%s])
        RETURN v_to._id as _id
        '''
        group_members = ','.join([str(v) for v in vs])
        task = (pattern % (group_members, group_members))
        return {int(r['_id'])`` for r in self.session.run(task).records()}

    def vertexes_related(self, v: int) -> Set[int]:
        pattern = '''
        MATCH (:Vertex {_id: %d})-[:Edge]-(v_related:Vertex)
        RETURN v_related._id as _id
        '''
        task = (pattern % (v))
        return {int(r['_id'])`` for r in self.session.run(task).records()}

    def vertexes_related_to_related(self, v: int, include_related=False) -> Set[int]:
        if include_related:
            pattern = '''
            MATCH (v:Vertex {_id: %d})-[:Edge]-(:Vertex)-[:Edge]-(v_unrelated:Vertex)
            WHERE NOT (v._id = v_unrelated._id)
            RETURN v_unrelated._id as _id
            '''
            task = (pattern % v)
        else:
            pattern = '''
            MATCH (v:Vertex {_id: %d})-[:Edge]-(:Vertex)-[:Edge]-(v_unrelated:Vertex)
            WHERE NOT EXISTS {
                MATCH (v)-[:Edge]-(v_unrelated)
            } AND NOT (v._id = v_unrelated._id)
            RETURN v_unrelated._id as _id
            '''
            task = (pattern % v)
        return {int(r['_id'])`` for r in self.session.run(task).records()}

    def shortest_path(self, v_from, v_to) -> (List[int], float):
        pattern = '''
        MATCH (v_from:Vertex {_id: %d}), (v_to:Vertex {_id: %d})
        CALL algo.shortestPath.stream(v_from, v_to, "weight")
        YIELD nodeId, weight
        MATCH (v_on_path:Loc) WHERE id(v_on_path) = nodeId
        RETURN v_on_path._id AS _id, weight
        '''
        rs = list(self.session.run(task).records())
        path = [int(r['_id']) for r in rs]
        weight = sum([float(r['weight']) for r in rs])
        return path, weight

    # Metadata

    def count_vertexes(self) -> int:
        task = '''
        MATCH (v:Vertex)
        WITH count(v) as result
        RETURN result
        '''
        return int(self._first_record(self.session.run(task), 'result'))

    def count_edges(self) -> int:
        task = '''
        MATCH ()-[e:Edge]->()
        WITH count(e) as result
        RETURN result
        '''
        return int(self._first_record(self.session.run(task), 'result'))

    def count_related(self, v: int) -> (int, float):
        pattern = '''
        MATCH (v:Vertex {_id: %d})-[e:Edge]-()
        WITH count(e) as c, sum(e.weight) as s
        RETURN c, s
        '''
        task = (pattern % v)
        rs = list(self.session.run(task).records())
        c = int(self._first_record(rs, 'c'))
        s = float(self._first_record(rs, 's'))
        return c, s

    def count_followers(self, v: int) -> (int, float):
        pattern = '''
        MATCH ()-[e:Edge]->(v:Vertex {_id: %d})
        WITH count(e) as c, sum(e.weight) as s
        RETURN c, s
        '''
        task = (pattern % v)
        rs = list(self.session.run(task).records())
        c = int(self._first_record(rs, 'c'))
        s = float(self._first_record(rs, 's'))
        return c, s

    def count_following(self, v: int) -> (int, float):
        pattern = '''
        MATCH (v:Vertex {_id: %d})-[e:Edge]->()
        WITH count(e) as c, sum(e.weight) as s
        RETURN c, s
        '''
        task = (pattern % v)
        rs = list(self.session.run(task).records())
        c = int(self._first_record(rs, 'c'))
        s = float(self._first_record(rs, 's'))
        return c, s

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
        task = str()
        if '_id' in e:
            pattern = '''
            MATCH ()-[e:Edge {_id: %d}]->()
            DELETE e
            '''
            task = (pattern % e['_id'])
        else:
            pattern = '''
            MATCH (v1:Vertex {_id: %d})
            MATCH (v2:Vertex {_id: %d})
            MERGE (v1)-[e:Edge]->(v2)
            DELETE e
            '''
            task = (pattern % (e['v_from'], e['v_to']))
        return self.session.run(task)

    def delete_all(self):
        try:
            self.session.run('DROP CONSTRAINT unique_nodes;')
        except:
            pass
        self.session.run('MATCH (v) DETACH DELETE v;')

    def _records_to_edges(self, records) -> List[Edge]:
        if isinstance(records, BoltStatementResult):
            records = list(records.records())
        return [Edge(r['v_from._id'], r['v_to._id'], r['e.weight']) for r in records]

    def _first_record(self, records, key):
        if isinstance(records, BoltStatementResult):
            records = list(records.records())
        if len(records) == 0:
            return None
        return records[0][key]


# wrap = Neo4j()
# print(wrap.insert(Edge(1, 3, 30)).keys())
# print(wrap.insert(Edge(1, 4, 40)).keys())
# print(wrap.insert(Edge(1, 5, 50)).keys())
# print(wrap.insert(Edge(1, 6, 60)).keys())
# print(wrap.insert(Edge(6, 7, 3)).keys())
# print(wrap.insert(Edge(7, 8, 3)).keys())
# print(wrap.edge_directed(1, 3))
# print(wrap.edges_related(1))
# print(wrap.count_vertexes())
# print(wrap.count_edges())
# print(wrap.count_related(1))
# print(wrap.count_followers(1))
# print(wrap.count_following(1))
# print(wrap.vertexes_related_to_group([7, 8]))
# print(wrap.vertexes_related_to_related(8))
