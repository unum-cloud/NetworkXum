import random
from random import SystemRandom
from typing import List

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
        self.edges_to_change_batched = [[]]
        self.count_finds = 10000
        self.count_analytics = 1000
        self.count_changes = 10000
        self._buffer_edges = list()

    def number_of_needed_samples(self) -> int:
        return max(self.count_finds,
                   self.count_analytics,
                   self.count_changes)

    def sample_reservoir(self, filename: str) -> int:
        self._buffer_edges = []
        count_seen = 0
        count_needed = self.number_of_needed_samples()
        for e in yield_edges_from(filename):
            count_seen += 1
            if len(self._buffer_edges) < count_needed:
                self._buffer_edges.append(e)
            else:
                s = int(random.random() * count_seen)
                if s < count_needed:
                    self._buffer_edges[s] = e
        self._split_samples_into_tasks()

    def sample_from_distribution(self, count_nodes):
        count_needed = self.number_of_needed_samples()
        while len(self._buffer_edges) < count_needed:
            v1 = random.randrange(1, count_nodes)
            v2 = random.randrange(1, count_nodes)
            if v1 == v2:
                continue
            self._buffer_edges.append({
                'v1': v1,
                'v2': v2,
            })
        self._split_samples_into_tasks()

    def sample_nodes_from_edges(self, cnt) -> List[int]:
        cnt = min(len(self._buffer_edges), cnt)
        es = random.sample(self._buffer_edges, cnt)
        # Save only unique values, but don't forget to shuffle.
        vs = {(e['v1'] if bool(random.getrandbits(1)) else e['v2'])
              for e in es}
        vs = list(vs)
        random.shuffle(vs)
        return vs

    def _split_samples_into_tasks(self):
        self.edges_to_query = random.sample(
            self._buffer_edges, self.count_finds)
        self.nodes_to_query = self.sample_nodes_from_edges(
            self.count_finds)
        self.nodes_to_analyze = self.sample_nodes_from_edges(
            self.count_analytics)
        self.edges_to_change_by_one = self._buffer_edges[:self.count_changes]
        self.edges_to_change_batched = list(chunks(
            self._buffer_edges[:self.count_changes],
            100,
        ))

        # Clear the memory
        # self._buffer_edges = None
        # self._select_nodes = None
