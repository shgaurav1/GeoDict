# coding=utf-8
from gzip import GzipFile
import json
class Reader(object):
    """docstring for Reader."""
    def __init__(self, name, decoding):
        #super(Reader, self).__init__()
        self.name = name
        self.decoding = decoding
        self.dump = GzipFile(name,'r')
        self.line = self.dump.readline()

    def has_next(self):
        self.line = self.dump.readline().decode(self.decoding)
        if self.line is '': return False
        else:return True

    def next(self):
        try:
            return json.loads(self.line.strip('\n,'))
        except json.decoder.JSONDecodeError as e:
            return None
