from PyWrappedHelpers.Algorithms import yield_texts_from_sectioned_csv, chunks
from P0Config import P0Config


class P3TasksSampler(object):
    """
        Select this data beforehand to:
        - avoid affecting the runtime of benchmark.
        - perform same "random" operations on different DBs.
    """

    def __init__(self):
        self.conf = P0Config.shared()
        self.count_substring_ops = self.conf.count_substring_ops
        self.count_regex_ops = self.conf.count_regex_ops
        self.count_changes = self.conf.count_changes
        self.clear()

    def clear(self):
        self.doc_ids_to_query = []
        self.substrings_to_query = []
        self.regexs_to_query = []
        self.docs_to_change_by_one = []
        self.docs_to_change_batched = [[]]
        self._buffer_texts = []

    def number_of_needed_samples(self) -> int:
        return self.count_changes

    def sample_file(self, filename: str) -> int:
        self.clear()
        self._buffer_texts = sample_reservoir(
            yield_texts_from_sectioned_csv(filename), self.number_of_needed_samples())
        self._split_samples_into_tasks()
        return len(self._buffer_texts)

    def _split_samples_into_tasks(self):

        all_ids = [t.path for t in self._buffer_texts]
        self.doc_ids_to_query = sample_reservoir(all_ids, self.count_changes)

        all_words = flatten([t.content.split() for t in self._buffer_texts])
        self.substrings_to_query = sample_reservoir(
            all_words, self.count_substring_ops)

        self.regexs_to_query = [

        ]
