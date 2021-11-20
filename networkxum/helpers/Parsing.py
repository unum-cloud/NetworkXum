from typing import List, Optional, Dict, Generator, Set, Tuple, Sequence, Generator
import csv
from pathlib import Path
import sys
import os.path

from PyStorageHelpers.Edge import Edge
from PyStorageHelpers.Text import Text


def allow_big_csv_fields():
    """
        When dealing with big docs in ElasticSearch - 
        an error may occur when bulk-loading:
        >>> _csv.Error: field larger than field limit (131072)        
    """
    max_field_len = sys.maxsize
    while True:
        # decrease the max_field_len value by factor 10
        # as long as the OverflowError occurs.
        # https://stackoverflow.com/a/15063941/2766161
        try:
            csv.field_size_limit(max_field_len)
            break
        except OverflowError:
            max_field_len = int(max_field_len/10)


# region Graphs

def yield_edges_from_csv(filepath: str, edge_type: type = Edge, is_directed=True) -> Generator[Edge, None, None]:
    with open(filepath, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        # Skip the header line.
        next(reader)
        for idx, row in enumerate(reader):
            if len(row) < 2:
                continue
            # Check if the data isn't corrupt.
            first = int(row[0])
            second = int(row[1])
            has_weight = (len(row) > 2 and len(row[2]) > 0)
            w = float(row[2]) if has_weight else 1.0
            yield edge_type(_id=idx, first=first, second=second, weight=w, is_directed=is_directed)


def import_graph(gdb, filepath: str) -> int:
    if filepath.endswith('.csv'):
        if hasattr(gdb, 'add_from_csv'):
            return gdb.add_from_csv(filepath)
        elif hasattr(gdb, 'add_stream'):
            return gdb.add_stream(yield_edges_from_csv(filepath, edge_type=type(gdb).__edge_type__))

    return 0
