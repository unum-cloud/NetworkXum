import os
import json
import copy


class TextFile(object):

    def __init__(self, path: str = '', content: str = ''):
        object.__init__(self)
        self.reset(path, content)

    def reset(self, path: str, content: str):
        self.path = path
        self.content_dict = dict()

        if len(content) == 0:
            if len(path) > 0:
                with open(path, 'r') as plain_file:
                    if path.endswith('.json'):
                        self.content_dict = json.load(plain_file)
                    else:
                        self.content_dict = {'plain': plain_file.read()}
            else:
                self.content_dict = {'plain': ''}
        else:
            self.content_dict = {'plain': content}

        if '_id' not in self.content_dict:
            self.content_dict['_id'] = os.path.basename(path)
        return self

    def is_empty(self) -> bool:
        return len(self.content_dict.get('plain', '')) == 0

    def to_dict(self) -> dict:
        d = copy.deepcopy(self.content_dict)
        if '_id' not in d:
            d['_id'] = self.path
        return d
