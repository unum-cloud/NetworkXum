import os
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Generator, Set, Tuple, Sequence
import concurrent.futures
from pathlib import Path

from PyWrappedDocs.TextFile import TextFile
from PyWrappedGraph.Algorithms import *


class BaseAPI(object):
    """
        Abstract base class for Documents Datastore.
        It's designed with JSON files in mind.
    """
    __max_batch_size__ = 500
    __is_concurrent__ = True
    __in_memory__ = False

    # --------------------------------
    # region: Initialization and Metadata.
    # --------------------------------

    def __init__(
        self,
        indexed_fields: Sequence[str] = ['plain'],
        **kwargs,
    ):
        object.__init__(self)
        self.indexed_fields = indexed_fields

    @abstractmethod
    def count_docs(self) -> int:
        pass

    # endregion

    # --------------------------------
    # region: Adding and removing documents.
    # --------------------------------

    @abstractmethod
    def upsert_doc(self, doc: object) -> bool:
        pass

    @abstractmethod
    def remove_doc(self, doc: object) -> bool:
        return False

    @abstractmethod
    def upsert_docs(self, docs: Sequence[object]) -> int:
        successes = map(self.upsert_doc, docs)
        return int(sum(successes))

    @abstractmethod
    def remove_docs(self, docs: Sequence[object]) -> int:
        successes = map(self.remove_doc, docs)
        return int(sum(successes))

    @abstractmethod
    def upsert_docs_from_directory(self, directory: str) -> int:
        cnt_success = 0
        paths = [pth for pth in Path(directory).iterdir()]
        for paths_chunk in chunks(paths, __max_batch_size__):
            files_chunk = map(TextFile, paths_chunk)
            cnt_success += self.upsert_docs(files_chunk)
        return cnt_success

    @abstractmethod
    def remove_all(self):
        pass

    # endregion

    # --------------------------------
    # region: Search Queries.
    # --------------------------------

    @abstractmethod
    def find_with_substring(self, field: str, query: str) -> Sequence[object]:
        pass

    @abstractmethod
    def find_with_regex(self, field: str, query: str) -> Sequence[object]:
        pass

    def find_by_id(self, identifier: str) -> object:
        pass

    # endregion
