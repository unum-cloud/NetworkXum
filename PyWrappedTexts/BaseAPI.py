import os
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Generator, Set, Tuple, Sequence
import concurrent.futures
from pathlib import Path

from PyWrappedHelpers import *


class BaseAPI(object):
    """
        Abstract base class for Documents Datastore.
        It's designed with JSON files in mind.
    """
    __max_batch_size__ = 1000
    __is_concurrent__ = True
    __in_memory__ = False

    # --------------------------------
    # region Initialization and Metadata.
    # --------------------------------

    def __init__(
        self,
        indexed_fields: Sequence[str] = ['content'],
        **kwargs,
    ):
        object.__init__(self)
        self.indexed_fields = indexed_fields

    @abstractmethod
    def count_texts(self) -> int:
        pass

    # endregion

    # --------------------------------
    # region Adding and removing documents.
    # --------------------------------

    @abstractmethod
    def upsert_text(self, doc: Text) -> bool:
        pass

    @abstractmethod
    def remove_text(self, doc: int) -> bool:
        return False

    @abstractmethod
    def upsert_texts(self, docs: Sequence[Text]) -> int:
        successes = map(self.upsert_text, docs)
        return int(sum(successes))

    @abstractmethod
    def remove_texts(self, docs: Sequence[int]) -> int:
        successes = map(self.remove_text, docs)
        return int(sum(successes))

    @abstractmethod
    def import_texts_from_directory(self, directory: str) -> int:
        cnt_success = 0
        paths = [pth for pth in Path(directory).iterdir()]
        for paths_chunk in chunks(paths, type(self).__max_batch_size__):
            files_chunk = map(Text, paths_chunk)
            cnt_success += self.upsert_texts(files_chunk)
        return cnt_success

    @abstractmethod
    def import_texts_from_csv(self, filepath: str) -> int:
        allow_big_csv_fields()
        cnt_success = 0
        for files_chunk in chunks(yield_texts_from_sectioned_csv(filepath), type(self).__max_batch_size__):
            cnt_success += self.upsert_texts(files_chunk)
        return cnt_success

    @abstractmethod
    def clear(self):
        pass

    # endregion

    # --------------------------------
    # region Search Queries.
    # --------------------------------

    @abstractmethod
    def find_with_id(self, id: int) -> object:
        pass

    @abstractmethod
    def find_with_substring(
        self,
        query: str,
        field: str = 'content',
        max_matches: int = None
    ) -> Sequence[Text]:
        pass

    @abstractmethod
    def find_with_regex(
        self,
        query: str,
        field: str = 'content',
        max_matches: int = None
    ) -> Sequence[Text]:
        pass

    # endregion
