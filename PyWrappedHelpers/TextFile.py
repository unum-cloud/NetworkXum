import os
import json
import copy


class TextFile(object):

    def __init__(self, path: str = '', content: str = ''):
        object.__init__(self)
        self.content = {}
        if isinstance(content, str) and len(content):
            self.path = path
            self.content['plain'] = content
        else:
            self.pull_from_path(path)

    def pull_from_path(self, path: str):
        self.path = path
        self.content = dict()

        if len(path):
            filename_w_ext = os.path.basename(path)
            self.content['_id'] = filename_w_ext
            if path.endswith('.txt'):
                with open(path, 'r') as plain_file:
                    self.content['plain'] = plain_file.read()
            elif path.endswith('.json'):
                with open(path, 'r') as plain_file:
                    self.content = json.load(plain_file)
            else:
                self.content['plain'] = ''
        else:
            self.content['plain'] = ''

        return self

    def to_dict(self) -> dict:
        d = copy.deepcopy(self.content)
        if '_id' not in d:
            d['_id'] = self.path
        return d
