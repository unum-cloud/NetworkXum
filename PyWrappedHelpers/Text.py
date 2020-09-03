import os
import hashlib
from dataclasses import dataclass


@dataclass
class Text:
    _id: int = -1
    content: str = ''

    @staticmethod
    def from_file(path: str, _id: int = None):
        text = Text()
        with open(path, 'r') as plain_file:
            if path.endswith('.json'):
                text.content = plain_file.read()
        if _id is None:
            text._id = hashlib.md5(os.path.basename(path))
        else:
            text._id = _id
        return text


@dataclass
class TextMatch(Text):
    rating: float = 1
