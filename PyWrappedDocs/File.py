import os
import json

class File(object):

    def __init__(self, path:str = ''):
        object.__init__(self)
        self.reset(path)

    def reset(self, path:str) -> File:        
        self.path = path
        self.content = dict()

        if len(path):    
            filename_w_ext = os.path.basename(path)
            if path.endswith('.txt'):
                with open(path, 'r') as plain_file:
                    self.content['plain'] = plain_file.read()
            elif path.endswith('.json'):
                with open(path, 'r') as plain_file:
                    self.content = json.load(plain_file)
            self.content['_id'] = filename_w_ext
        
        return self
            