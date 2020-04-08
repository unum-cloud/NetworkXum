import random
from random import SystemRandom

from pygraphdb.helpers import yield_edges_from, chunks


class TasksSampler(object):
    """
        Select this data beforehand to:
        - avoid affecting the runtime of benchmark.
        - perform same "random" operations on different DBs.
    """

    def __init__(self):
        self.edges_to_query = []
        self.nodes_to_query = []
        self.nodes_to_analyze = []
        self.edges_to_change_by_one = []
        self.nodes_to_change_by_one = []
        self.edges_to_change_batched = [[]]
        self.count_finds = 10000
        self.count_analytics = 1000
        self.count_changes = 10000
        self._select_edges = list()
        self._select_nodes = set()

    def sample_from_file(self, filename: str, sampling_ratio: float):
        rnd = SystemRandom()
        for e in yield_edges_from(filename):
            if rnd.random() < sampling_ratio:
                self._select_edges.append(e)
                self._select_nodes.add(e['v_from'])
        self._select_nodes = list(self._select_nodes)
        random.shuffle(self._select_edges)
        random.shuffle(self._select_nodes)
        self.count_finds = min(
            self.count_finds,
            len(self._select_nodes)
        )
        self.count_analytics = min(
            self.count_analytics,
            len(self._select_nodes)
        )
        self.count_changes = min(
            self.count_changes,
            len(self._select_edges)
        )
        self._split_samples()

    def sample_from_file_cpp(self, filename: str, sampling_ratio: float):
        pass

    def sample_from_distribution(self, count_nodes):
        count_max = max(self.count_finds,
                        self.count_analytics,
                        self.count_changes)
        while len(self._select_edges) < count_max:
            v_from = random.randrange(1, count_nodes)
            v_to = random.randrange(1, count_nodes)
            if v_from == v_to:
                continue
            if v_from in self._select_nodes:
                continue
            self._select_nodes.add(v_from)
            self._select_edges.append({
                'v_from': v_from,
                'v_to': v_to,
            })
        self._select_nodes = list(self._select_nodes)
        self._split_samples()

    def _split_samples(self):
        self.edges_to_query = random.sample(
            self._select_edges,
            self.count_finds,
        )
        self.nodes_to_query = random.sample(
            self._select_nodes,
            self.count_finds,
        )
        self.nodes_to_analyze = random.sample(
            self._select_nodes,
            self.count_analytics,
        )

        # Split write operations into groups.
        self.nodes_to_change_by_one = self._select_nodes[:self.count_changes]
        self.edges_to_change_by_one = self._select_edges[:self.count_changes]
        self.edges_to_change_batched = list(chunks(
            self._select_edges[:self.count_changes],
            100,
        ))

        # Clear the memory
        # self._select_edges = None
        # self._select_nodes = None
