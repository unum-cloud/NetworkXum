import os
import shutil
from typing import List, Set, Sequence
from urllib.parse import urlparse

from neo4j import GraphDatabase, Result as Neo4jResult

from networkxternal.base_api import BaseAPI
from networkxternal.helpers.edge import Edge
from networkxternal.helpers.algorithms import chunks, extract_database_name


class Neo4J(BaseAPI):
    """
    Uses Cypher DSL and Bolt API to access Neo4J graph database.

    ! WARNING 1:
    This is a suboptimal implementation in terms of space,
    as we can't overwrite the native node IDs with ours and have
    to index vertices by that artificial `_id` property.
    Furthermore, indexing edge properties is only available in
    enterprise edition, so querying edges by their ID can be even
    less then performant than searching them by connected node IDS.

    ! WARNING 2:
    Neo4J doesn't have easy switching mechanism between different
    databases on the same server. That's why we have to use "labels"
    to distinguish nodes and edges belonging to disjoint datasets,
    but mixed into the same pot.

    ! WARNING 3:
    Neo4J is written in Java (unlike most other DBs) and is very
    rude to other processes running on the same machine :)
    The CPU utilization is often 10-20x higher than in other DBs.
    To import 30 MB CSV file it allocated 1.4 GB of RAM!!!

    ! WARNING 4:
    It constantly crashes with different codes and included query
    profiler outputs inconsistent results. Examples:
    *   `neobolt.exceptions.TransientError:`
        There is not enough stack size to perform the current task.
        This is generally considered to be a database error,
        so please contact Neo4J support.
    *   `neobolt.exceptions.DatabaseError`
        Java heap space...
    """

    # Depending on the machine this can be higher.
    # But on a laptop we would get "Java heap space" error.
    __max_batch_size__ = 1000
    __is_concurrent__ = True
    __edge_type__ = Edge

    def __init__(
        self,
        url="bolt://localhost:7687/graph",
        enterprise_edition=False,
        import_directory="~/import",
        use_full_name_for_label=False,
        use_indexes_over_constraints=True,
        **kwargs,
    ):
        BaseAPI.__init__(self, **kwargs)
        self.import_directory = import_directory

        # Neo4J can't resolve DB name, username or password on its own.
        url_obj = urlparse(url)
        url_clean = "{x.scheme}://{x.hostname}:{x.port}/".format(x=url_obj)
        self.driver = GraphDatabase.driver(
            url_clean,
            auth=(url_obj.username, url_obj.password),
        )
        self.session = self.driver.session()

        # ! Resolve the name (for WARNING 2):
        name = str()
        _, c = extract_database_name(url)
        if (
            (c in "qwertyuiopasdfghjklzxcvbnm")
            or (c in "QWERTYUIOPAFGHJKLZXCVBNM")
            or (c in "1234567890")
        ):
            name += c
        self._v = "v" + name
        self._e = "e" + name
        # Create constraints if needed.
        self.use_indexes_over_constraints = use_indexes_over_constraints
        if use_indexes_over_constraints:
            indexes = self.get_indexes()
            if f"index{self._v}" not in indexes:
                self.create_index_nodes()
        else:
            cs = self.get_constraints()
            if f"constraint{self._v}" not in cs:
                self.create_constraint_nodes()
            if f"constraint{self._e}" not in cs:
                if enterprise_edition:
                    self.create_constraint_edges()

    def get_constraints(self) -> List[str]:
        cs = list(self.session.run("CALL db.constraints"))
        names = [c.get("name", "") for c in cs]
        return names

    def get_indexes(self) -> List[str]:
        cs = list(self.session.run("CALL db.indexes"))
        names = [c.get("name", "") for c in cs]
        return names

    def create_index_nodes(self):
        # Docs for CYPHER direct syntax:
        # https://neo4j.com/docs/cypher-manual/current/indexes-for-search-performance/#administration-indexes-syntax
        task = "CREATE INDEX indexVERTEX FOR (v:VERTEX) ON (v._id)"
        # Older version didn't have index names.
        # Docs for `db.` operations.
        # https://neo4j.com/docs/operations-manual/current/reference/procedures/#ref-procedure-reference-enterprise-edition
        # task = 'CALL db.createIndex(":VERTEX(_id)", "native-btree-1.0", )'
        task = task.replace("VERTEX", self._v)
        task = task.replace("EDGE", self._e)
        return self.session.run(task)

    def create_constraint_nodes(self):
        # Existing uniqueness constraint means,
        # that we don't have to create a separate index.
        # Docs: https://neo4j.com/docs/cypher-manual/current/administration/constraints/
        task = """
        CREATE CONSTRAINT constraintVERTEX
        ON (v:VERTEX)
        ASSERT (v._id) IS UNIQUE
        """
        task = task.replace("VERTEX", self._v)
        task = task.replace("EDGE", self._e)
        return self.session.run(task)

    def create_constraint_edges(self):
        # Edge uniqueness constrains are only available to Enterprise Edition customers.
        # https://neo4j.com/docs/cypher-manual/current/administration/constraints/#administration-constraints-syntax
        task = """
        CREATE CONSTRAINT uniqueEDGE
        ON ()-[e:EDGE]-()
        ASSERT (e._id) IS UNIQUE
        """
        # Indexes on relationships are not implemented yet.
        # https://stackoverflow.com/a/22444108
        # task = '''
        # CREATE INDEX ids_edges
        # FOR [e:EDGE]
        # ON (e._id)
        # '''
        task = task.replace("VERTEX", self._v)
        task = task.replace("EDGE", self._e)
        return self.session.run(task)

    # Relatives

    def has_edge(self, first: int, second: int, **kwargs) -> List[Edge]:
        if self.directed:
            pattern = """
            MATCH (first:VERTEX {_id: %d})-[e:EDGE]->(second:VERTEX {_id: %d})
            RETURN first._id, second._id, e.weight
            """
        else:
            pattern = """
            MATCH (first:VERTEX {_id: %d})-[e:EDGE]-(second:VERTEX {_id: %d})
            RETURN first._id, second._id, e.weight
            """
        task = pattern % (first, second)
        task = task.replace("VERTEX", self._v)
        task = task.replace("EDGE", self._e)
        return self._records_to_edges(self.session.run(task))

    def edges_from(self, v: int) -> List[Edge]:
        pattern = """
        MATCH (first:VERTEX {_id: %d})-[e:EDGE]->(second:VERTEX)
        RETURN first._id, second._id, e.weight
        """
        task = pattern % (v)
        task = task.replace("VERTEX", self._v)
        task = task.replace("EDGE", self._e)
        return self._records_to_edges(self.session.run(task))

    def edges_to(self, v: int) -> List[Edge]:
        pattern = """
        MATCH (first:VERTEX)-[e:EDGE]->(second:VERTEX {_id: %d})
        RETURN first._id, second._id, e.weight
        """
        task = pattern % (v)
        task = task.replace("VERTEX", self._v)
        task = task.replace("EDGE", self._e)
        return self._records_to_edges(self.session.run(task))

    def edges_related(self, v: int) -> List[Edge]:
        pattern = """
        MATCH (first:VERTEX {_id: %d})-[e:EDGE]-(second:VERTEX)
        RETURN first._id, second._id, e.weight
        """
        task = pattern % (v)
        task = task.replace("VERTEX", self._v)
        task = task.replace("EDGE", self._e)
        return self._records_to_edges(self.session.run(task))

    # Wider range of neighbors

    def edges_related_to_group(self, vs: Sequence[int]) -> List[Edge]:
        pattern = """
        MATCH (first:VERTEX)-[e:EDGE]-(second:VERTEX)
        WHERE (first._id IN [%s]) AND NOT (second._id IN [%s])
        RETURN first._id, second._id, e.weight
        """
        group_members = ",".join([str(v) for v in vs])
        task = pattern % (group_members, group_members)
        task = task.replace("VERTEX", self._v)
        task = task.replace("EDGE", self._e)
        return self._records_to_edges(self.session.run(task))

    def neighbors_of_group(self, vs: Sequence[int]) -> Set[int]:
        pattern = """
        MATCH (first:VERTEX)-[:EDGE]-(second:VERTEX)
        WHERE (first._id IN [%s]) AND NOT (second._id IN [%s])
        RETURN second._id as _id
        """
        group_members = ",".join([str(v) for v in vs])
        task = pattern % (group_members, group_members)
        task = task.replace("VERTEX", self._v)
        task = task.replace("EDGE", self._e)
        return {int(r["_id"]) for r in self.session.run(task)}

    def neighbors(self, v: int) -> Set[int]:
        pattern = """
        MATCH (:VERTEX {_id: %d})-[:EDGE]-(v_related:VERTEX)
        RETURN v_related._id as _id
        """
        task = pattern % (v)
        task = task.replace("VERTEX", self._v)
        task = task.replace("EDGE", self._e)
        return {int(r["_id"]) for r in self.session.run(task)}

    def neighbors_of_neighbors(self, v: int, include_related=False) -> Set[int]:
        if include_related:
            pattern = """
            MATCH (v:VERTEX {_id: %d})-[:EDGE]-(:VERTEX)-[:EDGE]-(v_unrelated:VERTEX)
            WHERE NOT (v._id = v_unrelated._id)
            RETURN v_unrelated._id as _id
            """
            task = pattern % v
        else:
            pattern = """
            MATCH (v:VERTEX {_id: %d})-[:EDGE]-(:VERTEX)-[:EDGE]-(v_unrelated:VERTEX)
            WHERE NOT EXISTS {
                MATCH (v)-[e_banned:EDGE]-(v_unrelated)
            } AND NOT (v._id = v_unrelated._id)
            RETURN v_unrelated._id as _id
            """
            task = pattern % v
        task = task.replace("VERTEX", self._v)
        task = task.replace("EDGE", self._e)
        return {int(r["_id"]) for r in self.session.run(task)}

    def shortest_path(self, first, second) -> (List[int], float):
        pattern = """
        MATCH (first:VERTEX {_id: %d}), (second:VERTEX {_id: %d})
        CALL algo.shortestPath.stream(first, second, "weight")
        YIELD nodeId, weight
        MATCH (v_on_path:Loc) WHERE id(v_on_path) = nodeId
        RETURN v_on_path._id AS _id, weight
        """
        task = pattern % (first, second)
        task = task.replace("VERTEX", self._v)
        task = task.replace("EDGE", self._e)
        rs = list(self.session.run(task))
        path = [int(r["_id"]) for r in rs]
        weight = sum([float(r["weight"]) for r in rs])
        return path, weight

    # Metadata

    def reduce_nodes(self) -> int:
        task = f"""
        MATCH (v:{self._v})
        WITH count(v) as result
        RETURN result
        """
        return int(self._first_record(self.session.run(task), "result"))

    def reduce_edges(self, **kwargs) -> int:
        task = f"""
        MATCH ()-[e:{self._e}]->()
        WITH count(e) as result
        RETURN result
        """
        return int(self._first_record(self.session.run(task), "result"))

    def degree_neighbors(self, v: int) -> int | float:
        pattern = """
        MATCH (v:VERTEX {_id: %d})-[e:EDGE]-()
        WITH count(e) as c, sum(e.weight) as s
        RETURN c, s
        """
        task = pattern % v
        task = task.replace("VERTEX", self._v)
        task = task.replace("EDGE", self._e)
        rs = list(self.session.run(task))
        c = int(self._first_record(rs, "c"))
        s = float(self._first_record(rs, "s"))
        return c, s

    def degree_predecessors(self, v: int) -> int | float:
        pattern = """
        MATCH (:VERTEX)-[e:EDGE]->(v:VERTEX {_id: %d})
        WITH count(e) as c, sum(e.weight) as s
        RETURN c, s
        """
        task = pattern % v
        task = task.replace("VERTEX", self._v)
        task = task.replace("EDGE", self._e)
        rs = list(self.session.run(task))
        c = int(self._first_record(rs, "c"))
        s = float(self._first_record(rs, "s"))
        return c, s

    def degree_successors(self, v: int) -> int | float:
        pattern = """
        MATCH (v:VERTEX {_id: %d})-[e:EDGE]->(:VERTEX)
        WITH count(e) as c, sum(e.weight) as s
        RETURN c, s
        """
        task = pattern % v
        task = task.replace("VERTEX", self._v)
        task = task.replace("EDGE", self._e)
        rs = list(self.session.run(task))
        c = int(self._first_record(rs, "c"))
        s = float(self._first_record(rs, "s"))
        return c, s

    def biggest_edge_id(self) -> int:
        task = """
        MATCH (:VERTEX)-[e:EDGE]->(:VERTEX)
        RETURN e._id AS _id
        ORDER BY _id DESC
        LIMIT 1
        """
        task = task.replace("VERTEX", self._v)
        task = task.replace("EDGE", self._e)
        rs = list(self.session.run(task))
        if len(rs) == 0:
            return 0
        return int(self._first_record(rs, "_id"))

    def add(self, e: Edge, **kwargs) -> bool:
        """
        WARNING: True "upserting" is too slow, if indexing isn't enabled,
        as we need to perform full scans to match each edge ID!
        So for the non-enterprise version - we strongly recommend
        using `insert_edge()`
        """
        pattern = """
        MERGE (first:VERTEX {_id: %d})
        MERGE (second:VERTEX {_id: %d})
        MERGE (first)-[:EDGE {_id: %d, weight: %d}]%s(second)
        """
        d = "->" if e.is_directed else "-"
        task = pattern % (e.first, e.second, e._id, e.weight, d)
        task = task.replace("VERTEX", self._v)
        task = task.replace("EDGE", self._e)
        self.session.run(task)
        return True

    def insert_edge(self, e: Edge) -> bool:
        pattern = """
        MERGE (first:VERTEX {_id: %d})
        MERGE (second:VERTEX {_id: %d})
        CREATE (first)-[:EDGE {_id: %d, weight: %d}]%s(second)
        """
        d = "->" if e.is_directed else "-"
        task = pattern % (e.first, e.second, e._id, e.weight, d)
        task = task.replace("VERTEX", self._v)
        task = task.replace("EDGE", self._e)
        self.session.run(task)
        return True

    def insert_edges(self, es: List[Edge]) -> int:
        vs = set()
        for e in es:
            vs.add(e.first)
            vs.add(e.second)
        task = str()
        # First upsert all the nodes.
        for v in vs:
            pattern = "MERGE (v%d:VERTEX {_id: %d})"
            part = pattern % (v, v)
            task += part
            task += "\n"
        # Then add the edges connecting matched nodes.
        for e in es:
            pattern = "CREATE (v%d)-[:EDGE {_id: %d, weight: %d}]%s(v%d)"
            d = "->" if e.is_directed else "-"
            part = pattern % (e.first, e._id, e.weight, d, e.second)
            task += part
            task += "\n"
        task = task.replace("VERTEX", self._v)
        task = task.replace("EDGE", self._e)
        self.session.run(task)
        return len(es)

    def remove_node(self, v: int):
        pattern = """
        MATCH (v:VERTEX {_id: %d})
        DETACH DELETE v
        """
        task = pattern % v
        task = task.replace("VERTEX", self._v)
        task = task.replace("EDGE", self._e)
        return self.session.run(task)

    def remove(self, e: Edge) -> bool:
        task = str()
        if e._id < 0:
            pattern = """
            MATCH (first:VERTEX {_id: %d})
            MATCH (second:VERTEX {_id: %d})
            MATCH (first)-[e:EDGE]%s(second)
            DELETE e
            """
            d = "->" if e.is_directed else "-"
            task = pattern % (e.first, e.second, d)
        else:
            # We provide excessive information on node IDs
            # to use property indexes.
            pattern = """
            MATCH (first:VERTEX {_id: %d})
            MATCH (second:VERTEX {_id: %d})
            MATCH (first)-[e:EDGE {_id: %d}]%s(second)
            DELETE e
            """
            d = "->" if e.is_directed else "-"
            task = pattern % (e.first, e.second, e._id, d)
        task = task.replace("VERTEX", self._v)
        task = task.replace("EDGE", self._e)
        self.session.run(task)
        return True

    def clear(self):
        self.session.run(f"MATCH (v:{self._v}) DETACH DELETE v")
        idxs = self.get_indexes()
        if f"index{self._v}" in idxs:
            self.session.run(f"DROP INDEX index{self._v}")
        cs = self.get_constraints()
        if f"constraint{self._v}" in cs:
            self.session.run(f"DROP CONSTRAINT constraint{self._v}")
        if f"constraint{self._e}" in cs:
            self.session.run(f"DROP CONSTRAINT constraint{self._e}")

    def add_stream(self, stream, **kwargs) -> int:
        chunk_len = Neo4J.__max_batch_size__
        count_edges_added = 0
        for es in chunks(stream, chunk_len):
            count_edges_added += self.insert_edges(es)
        return count_edges_added

    def add_from_csv(self, filepath: str, is_directed=True) -> int:
        """
        This function may be tricky to use!

        ! WARNING 1: This operation makes a temporary copy of the entire dump
        ! and places it into pre-specified `import_directory`:
        ! https://neo4j.com/docs/operations-manual/4.0/configuration/file-locations/

        ! WARNING 2: This frequently fails with following error:
        ! `neobolt.exceptions.DatabaseError`: "Java heap space".
        """
        cnt = self.number_of_edges()
        current_id = self.biggest_edge_id() + 1
        _, filename = os.path.split(filepath)

        # We will need to link the file to import folder.
        file_link = os.path.expanduser(self.import_directory)
        file_link = os.path.join(file_link, filename)
        file_link = os.path.abspath(file_link)

        try:
            shutil.copy(filepath, file_link)
            # https://neo4j.com/docs/cypher-manual/current/clauses/load-csv/#load-csv-importing-large-amounts-of-data
            pattern_full = """
            LOAD CSV WITH HEADERS FROM '%s' AS row
            WITH
                toInteger(row.first) AS id_from,
                toInteger(row.second) AS id_to,
                toFloat(row.weight) AS w,
                toInteger(linenumber()) AS idx
            MERGE (first:VERTEX {_id: id_from})
            MERGE (second:VERTEX {_id: id_to})
            CREATE (first)-[:EDGE {_id: idx + %d, weight: w}]%s(second)
            """
            d = "->" if is_directed else "-"
            task = pattern_full % ("file:///" + filename, current_id, d)
            task = task.replace("VERTEX", self._v)
            task = task.replace("EDGE", self._e)
            print("task is:", task)
            self.session.run(task)
        finally:
            # Don't forget to copy temporary file!
            os.unlink(file_link)
        return self.number_of_edges() - cnt

    def insert_adjacency_list_in_parts(self, filepath: str, is_directed=True) -> int:
        """
        This function may be tricky to use!

        ! WARNING 1: This operation makes a temporary copy of the entire dump
        ! and places it into pre-specified `import_directory`:
        ! https://neo4j.com/docs/operations-manual/4.0/configuration/file-locations/

        ! WARNING 2: This frequently fails with following error:
        ! `neobolt.exceptions.DatabaseError`: "Java heap space".
        """
        cnt = self.number_of_edges()
        current_id = self.biggest_edge_id() + 1
        _, filename = os.path.split(filepath)

        # We will need to link the file to import folder.
        file_link = os.path.expanduser(self.import_directory)
        file_link = os.path.join(file_link, filename)
        file_link = os.path.abspath(file_link)

        try:
            shutil.copy(filepath, file_link)
            # https://neo4j.com/docs/cypher-manual/current/clauses/load-csv/#load-csv-importing-large-amounts-of-data
            pattern_nodes = """
            USING PERIODIC COMMIT %d
            LOAD CSV WITH HEADERS FROM '%s' AS row
            WITH
                toInteger(row.first) AS id_from,
                toInteger(row.second) AS id_to
            MERGE (first:VERTEX {_id: id_from})
            MERGE (second:VERTEX {_id: id_to});
            """
            pattern_edges = """
            USING PERIODIC COMMIT %d
            LOAD CSV WITH HEADERS FROM '%s' AS row
            WITH
                toInteger(row.first) AS id_from,
                toInteger(row.second) AS id_to,
                toFloat(row.weight) AS w,
                toInteger(linenumber()) AS idx
            MATCH (first:VERTEX {_id: id_from})
            MATCH (second:VERTEX {_id: id_to})
            CREATE (first)-[e:EDGE {_id: idx + %d, weight: w}]%s(second)
            RETURN count(e)
            """
            d = "->" if is_directed else "-"
            tasks = [
                pattern_nodes % (Neo4J.__max_batch_size__, "file:///" + filename),
                pattern_edges
                % (Neo4J.__max_batch_size__, "file:///" + filename, current_id, d),
            ]
            for task in tasks:
                task = task.replace("VERTEX", self._v)
                task = task.replace("EDGE", self._e)
                self.session.run(task)
        finally:
            # Don't forget to copy temporary file!
            os.unlink(file_link)
        return self.number_of_edges() - cnt

    # ---
    # Helper methods.
    # ---

    def _records_to_edges(self, records) -> List[Edge]:
        if isinstance(records, Neo4jResult):
            records = list(records)
        return [Edge(r["first._id"], r["second._id"], r["e.weight"]) for r in records]

    def _first_record(self, records, key):
        if isinstance(records, Neo4jResult):
            records = list(records)
        if len(records) == 0:
            return None
        return records[0][key]
