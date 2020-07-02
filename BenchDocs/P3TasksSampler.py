from PyWrappedHelpers.Algorithms import *
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
        self.words_to_search = []
        self.phrases_to_search = []
        self.regexs_to_search = []
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

        all_words = flatten([t.to_dict().pop('plain', '').split()
                             for t in self._buffer_texts])
        self.words_to_search = sample_reservoir(
            all_words, self.count_substring_ops)
        self.docs_to_change_by_one = self._buffer_texts
        self.docs_to_change_batched = list(chunks(self._buffer_texts, 500))
        self.regexs_to_search = [
            # Example: +1(999)88-999-1234 5678
            ('phone', "[+][0-9]{0,3}[( ]?[0-9]{1,4}[) ]?[\\-\\s\\./0-9]*"),
            # Example: a@unum.xyz
            ('email', "[A-Za-z0-9\\._]+@[A-Za-z0-9]+\\.[a-z]{2,6}"),
            # Example: 23/02/2015
            ('date_slash', "\\d{2}/\\d{2}/\\d{4}"),
            # Example: 23-02 234 BCE
            ('date',
             "\\d{1,2}[./:\\-, ]\\d{1,2}[./:\\-, ]\\d{1,4}[ ]?(CE|BCE|BC|AD)?"),
            # Examples: 04:30, 21:55 am
            ('time', "[0-2][0-9]:[0-5][0-9][ ]?(am|pm)?"),
            # Example: 255.255.255.255
            # https://www.regular-expressions.info/ip.html
            ('ipv4',
             "\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}"),
            # Example: < br/>
            ('xmltag', "<[a-z]*/?>"),
            # Example: " "
            ('word_delimeters', "[ .!?]"),
        ]

        w0s = sample_reservoir(all_words, self.count_substring_ops)
        w1s = sample_reservoir(all_words, self.count_substring_ops)
        self.phrases_to_search = [
            f'{w0s[i]} {w1s[i]}' for i in range(self.count_substring_ops)]
