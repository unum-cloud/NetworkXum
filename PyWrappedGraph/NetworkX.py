
class NetworkX(object):

    # --------------------------------
    # region: Adding and removing nodes and edges.
    # https://networkx.github.io/documentation/stable/reference/classes/graph.html#adding-and-removing-nodes-and-edges
    # --------------------------------

    def __init__(self, graph_db):
        self.db = self.graph_db

    def add_edge(self, u: int, v: int, **attrs) -> bool:
        """https://networkx.github.io/documentation/stable/reference/classes/generated/networkx.Graph.upsert_edge.html#networkx.Graph.add_edge"""
        return self.upsert_edge(Edge(first=u, second=v, **attrs))

    def add_edges_from(self, es, **attrs) -> int:
        """https://networkx.github.io/documentation/stable/reference/classes/generated/networkx.Graph.add_edges_from.html#networkx.Graph.add_edges_from"""
        for e in es:
            self.add_edge(e, **attrs)

    def add_node(self, n: int, **attr) -> bool:
        """https://networkx.github.io/documentation/stable/reference/classes/generated/networkx.Graph.add_node.html#networkx.Graph.add_node"""
        self.db.insert_node(n, **attr)

    def remove_edge(self, u: int, v: int) -> bool:
        """https://networkx.github.io/documentation/stable/reference/classes/generated/networkx.Graph.remove_edge.html#networkx.Graph.remove_edge"""
        self.db.remove_edge(Edge(u, v))

    def remove_edges_from(self, es: List[Edge]) -> int:
        """https://networkx.github.io/documentation/stable/reference/classes/generated/networkx.Graph.remove_edges_from.html#networkx.Graph.remove_edges_from"""
        for e in es:
            self.remove_edge(e)

    @abstractmethod
    def clear(self):
        """https://networkx.github.io/documentation/stable/reference/classes/generated/networkx.Graph.clear.html#networkx.Graph.clear"""
        self.db.remove_all()

    @abstractmethod
    def remove_node(self, n: int) -> int:
        """https://networkx.github.io/documentation/stable/reference/classes/generated/networkx.Graph.remove_node.html#networkx.Graph.remove_node"""
        self.db.remove_node(n)

    @abstractmethod
    def remove_nodes_from(self, vs: list) -> int:
        """https://networkx.github.io/documentation/stable/reference/classes/generated/networkx.Graph.remove_nodes_from.html#networkx.Graph.remove_nodes_from"""
        for v in vs:
            self.remove_node(v)

    @abstractmethod
    def new_edge_key(self, u: int, v: int) -> int:
        """https://networkx.github.io/documentation/stable/reference/classes/generated/networkx.MultiDiGraph.new_edge_key.html#networkx.MultiDiGraph.new_edge_key"""
        return Edge.identify_by_members(u, v)

    # endregion

    # --------------------------------
    # region: Reporting nodes edges and neighbors.
    # https://networkx.github.io/documentation/stable/reference/classes/graph.html#reporting-nodes-edges-and-neighbors
    # --------------------------------

    @abstractmethod
    def edge_directed(self, first: int, second: int) -> Optional[Edge]:
        """
            Given 2 vertexes that are stored in DB as 
            outgoing from `first` into `second`.
        """
        pass

    @abstractmethod
    def edge_undirected(self, first: int, second: int) -> Optional[Edge]:
        """
            Given 2 vertexes search for an edge 
            that goes in any direction.
        """
        pass

    @abstractmethod
    def edges_from(self, v: int) -> List[Edge]:
        pass

    @abstractmethod
    def edges_to(self, v: int) -> List[Edge]:
        pass

    @abstractmethod
    def edges_related(self, v: int) -> List[Edge]:
        """
            Finds all edges that contain `v` as part of it.
        """
        pass
    # endregion

    # Metadata

    @abstractmethod
    def count_nodes(self) -> int:
        pass

    @abstractmethod
    def count_edges(self) -> int:
        pass

    @abstractmethod
    def count_related(self, v: int) -> (int, float):
        """
            Returns
            -------
            int 
                The number of edges containing `v`.
            float
                The total `weight` of edges containing `v`
        """
        pass

    @abstractmethod
    def count_followers(self, v: int) -> (int, float):
        """
            Returns
            -------
            int 
                The number of edges incoming into `v`.
            float
                The total `weight` of edges incoming into `v`.
        """
        pass

    @abstractmethod
    def count_following(self, v: int) -> (int, float):
        """
            Returns
            -------
            int 
                The number of edges outgoing from `v`.
            float
                The total `weight` of edges outgoing from `v`.
        """
        pass

    # Modifications

    # Needed only for compatiability with with NetworkX.
    # Iterate over the nodes.
    # https://networkx.github.io/documentation/stable/reference/classes/generated/networkx.Graph.__iter__.html#networkx.Graph.__iter__
    def __iter__(self):
        pass

    # Needed only for compatiability with with NetworkX.
    # Returns the number of nodes in the graph.
    # https://networkx.github.io/documentation/stable/reference/classes/generated/networkx.Graph.__len__.html#networkx.Graph.__len__
    def __len__(self) -> int:
        return self.count_nodes()

    # Needed only for compatiability with with NetworkX.
    # Returns the number of nodes in the graph.
    # https://networkx.github.io/documentation/stable/reference/classes/generated/networkx.Graph.number_of_nodes.html#networkx.Graph.number_of_nodes
    def number_of_nodes(self) -> int:
        return self.count_nodes()

    # Needed only for compatiability with with NetworkX.
    # Returns the number of nodes in the graph.
    # https://networkx.github.io/documentation/stable/reference/classes/generated/networkx.Graph.order.html#networkx.Graph.order
    def order(self) -> int:
        return self.count_nodes()

    # Needed only for compatiability with with NetworkX.
    # Returns the number of edges or total of all edge weights.
    # https://networkx.github.io/documentation/stable/reference/classes/generated/networkx.Graph.size.html#networkx.Graph.size
    def size(self, weight=None):
        pass

    # Needed only for compatiability with with NetworkX.
    # Returns the number of edges between two nodes.
    # https://networkx.github.io/documentation/stable/reference/classes/generated/networkx.Graph.number_of_nodes.html#networkx.Graph.number_of_edges
    def number_of_edges(self, u=None, v=None) -> int:
        if (u is None) and (v is None):
            return self.count_edges()
        e = self.edge_directed(u, v)
        return 0 if (e is None) else 1

    # Needed only for compatiability with with NetworkX.
    # Returns the attribute dictionary associated with edge `(u, v)`.
    # https://networkx.github.io/documentation/stable/reference/classes/generated/networkx.Graph.get_edge_data.html#networkx.Graph.get_edge_data
    def get_edge_data(self, u, v) -> dict:
        e = self.edge_directed(u, v)
        return None if (e is None) else e.__dict__

    # Needed only for compatiability with with NetworkX.
    # Returns a dict of neighbors of node n.
    # https://networkx.github.io/documentation/stable/reference/classes/generated/networkx.Graph.__getitem__.html#networkx.Graph.__getitem__
    def __getitem__(self, n) -> dict:
        pass

    # --------------------------------
    # Wider range of neighbors.
    # --------------------------------

    @abstractmethod
    def nodes_related(self, v: int) -> Set[int]:
        """
            Returns the IDs of all vertexes that have a shared edge with `v`.
        """
        vs_unique = set()
        for e in self.edges_related(v):
            vs_unique.add(e.first)
            vs_unique.add(e.second)
        vs_unique.discard(v)
        return vs_unique

    @abstractmethod
    def nodes_related_to_group(self, vs: Sequence[int]) -> Set[int]:
        """
            Returns the IDs of all vertexes that have at 
            least one shared edge with any member of `vs`.
        """
        results = set()
        for v in vs:
            results = results.union(self.nodes_related(v))
        return results.difference(set(vs))

    @abstractmethod
    def nodes_related_to_related(self, v: int, include_related=False) -> Set[int]:
        related = self.nodes_related(v)
        related_to_related = self.nodes_related_to_group(related.union({v}))
        if include_related:
            return related_to_related.union(related).difference({v})
        else:
            return related_to_related.difference(related).difference({v})

    @abstractmethod
    def shortest_path(self, first, second) -> List[int]:
        pass
