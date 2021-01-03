import random

from PyStorageHelpers import *
from P0Config import P0Config


class P3TasksSampler(object):
    """
        Select this data beforehand to:
        - avoid affecting the runtime of benchmark.
        - perform same "random" operations on different DBs.
    """
    __regex_templates__ = [
        {
            "Name": "A Phone Number + Random Word",
            "Example": "+1(999)88-999-1234 5678 RANDOM",
            "Template": r"[+][0-9]{0,3}[( ]?[0-9]{1,4}[) ]?[\-\s\./0-9]* ${RANDOM}",
            "Tasks": [],
        },
        {
            "Name": "An Email at Random Domain",
            "Example": "employee@RANDOM.com",
            "Template": r"[A-Za-z0-9\._]+@${RANDOM}\.[a-z]{2, 6}",
            "Tasks": [],
        },
        {
            "Name": "A Date + Random Word",
            "Example": "23/02/2015 RANDOM",
            "Template": r"\d{2}/\d{2}/\d{4} ${RANDOM}",
            "Tasks": [],
        },
        {
            "Name": "A Complex Date Pattern + Random Word",
            "Example": "23-02 234 BCE RANDOM",
            "Template": r"\d{1, 2}[./:\-, ]\d{1, 2}[./:\-, ]\d{1, 4}[]?(CE|BCE|BC|AD)? ${RANDOM}",
            "Tasks": [],
        },
        {
            "Name": "A Time + Random Word",
            "Example": "04:30, 21:55 am RANDOM",
            "Template": r"[0-2][0-9]:[0-5][0-9][ ]?(am|pm)? ${RANDOM}",
            "Tasks": [],
        },
        {
            "Name": "An IPv4 Address with Random Page",
            "Example": "255.255.255.255/RANDOM",
            "Template": r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/${RANDOM}",
            "Tasks": [],
        },
        {
            "Name": "Random Word in XML Tag",
            "Example": "<table>RANDOM</table>",
            "Template": r"<[a-z]*/?>${RANDOM}<[a-z]*/?>",
            "Tasks": [],
        },
    ]

    def __init__(self):
        self.conf = P0Config.shared()
        self.count_substring_ops = self.conf.count_substring_ops
        self.count_regex_ops = self.conf.count_regex_ops
        self.count_changes = self.conf.count_changes
        self.clear()

    def clear(self):
        self.doc_ids_to_query = []
        self.short_words_to_search = []
        self.short_phrases_to_search = []
        self.regexs_to_search = []
        self.docs_to_change_by_one = []
        self.docs_to_change_batched = [[]]
        self._buffer_texts = []

    def number_of_needed_samples(self) -> int:
        return self.count_changes * 10

    def sample_file(self, filename: str) -> int:
        self.clear()
        self._buffer_texts = sample_reservoir(
            yield_texts_from_csv(filename), self.number_of_needed_samples())
        self._split_samples_into_tasks()
        return len(self._buffer_texts)

    def _split_samples_into_tasks(self):

        all_ids = [t._id for t in self._buffer_texts]
        self.doc_ids_to_query = sample_reservoir(all_ids, self.count_changes)

        all_words = flatten([t.content.split() for t in self._buffer_texts])
        all_words = filter(lambda x: x.isalnum(), all_words)
        all_words = list([x.lower() for x in all_words])
        cnt_wanted = min(self.count_substring_ops, len(all_words))

        self.short_words_to_search = sample_reservoir(
            [x for x in all_words if (len(x) > 6 and len(x) < 9)], self.count_substring_ops)
        self.long_words_to_search = sample_reservoir(
            [x for x in all_words if (len(x) > 9)], self.count_substring_ops)
        self.docs_to_change_by_one = self._buffer_texts[:self.count_changes]
        self.docs_to_change_batched = list(
            chunks(self._buffer_texts[:self.count_changes], 500))

        # We add random words to avoid cache matches.
        self.regexs_to_search = type(self).__regex_templates__
        ws_regex = sample_reservoir(all_words, cnt_wanted)
        for family in self.regexs_to_search:
            template = family['Template']
            for i, w in enumerate(ws_regex):
                w_regex = template.replace(r"${RANDOM}", ws_regex[i])
                family['Tasks'].append(w_regex)

        self.short_phrases_to_search = [
            f'{random.choice(self.short_words_to_search)} {random.choice(self.short_words_to_search)}' for _ in range(self.count_substring_ops)]
        self.long_phrases_to_search = [
            f'{random.choice(self.long_words_to_search)} {random.choice(self.long_words_to_search)}' for _ in range(self.count_substring_ops)]
