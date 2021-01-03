import os
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Generator, Set, Tuple, Sequence
import concurrent.futures
import collections

from PyStorageHelpers import *


class BaseAPI(object):
    """
        Abstract base class for Documents Datastore.
        It's designed with JSON files in mind.
    """
    __max_batch_size__ = 1000
    __is_concurrent__ = True
    __in_memory__ = False

# region Metadata

    def __init__(self, **kwargs):
        object.__init__(self)
        self.indexed_fields = ['content']

    @abstractmethod
    def count_texts(self) -> int:
        return 0


# region Random Writes

    @abstractmethod
    def add(self, one_or_many_texts, upsert=True) -> int:
        if isinstance(one_or_many_texts, collections.Sequence):
            return int(sum(map(self.add, one_or_many_texts)))
        elif isinstance(one_or_many_texts, Text):
            return self.add([one_or_many_texts])
        elif isinstance(one_or_many_texts, dict):
            return self.add(Text(**one_or_many_texts))
        return False

    @abstractmethod
    def remove(self, one_or_many_texts) -> int:
        if isinstance(one_or_many_texts, collections.Sequence):
            return int(sum(map(self.remove, one_or_many_texts)))
        elif isinstance(one_or_many_texts, Text):
            return self.remove(one_or_many_texts._id)
        elif isinstance(one_or_many_texts, dict):
            return self.remove(one_or_many_texts.pop('_id', None))
        return False


# region Bulk Writes

    @abstractmethod
    def add_stream(self, stream, upsert=False) -> int:
        cnt_success = 0
        for texts_batch in chunks(stream, type(self).__max_batch_size__):
            try:
                cnt_success += self.add(texts_batch, upsert=upsert)
            except:
                pass
        return cnt_success

    @abstractmethod
    def clear(self):
        pass

# region Random Reads

    @abstractmethod
    def get(self, id: int) -> Optional[Text]:
        return None

    @abstractmethod
    def find_substring(
        self,
        query: str,
        case_sensitive: bool = True,
        max_matches: Optional[int] = None,
        include_text=True,
    ) -> Sequence[Text]:
        return []

    @abstractmethod
    def find_regex(
        self,
        query: str,
        case_sensitive: bool = True,
        max_matches: Optional[int] = None,
        include_text=True,
    ) -> Sequence[Text]:
        return []

# region Bulk Reads

    @property
    @abstractmethod
    def texts(self) -> Sequence[Text]:
        return []
