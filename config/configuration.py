# coding = utf-8

import json

class Configuration(dict):
    def __init__(self, input_file):
        super(Configuration,dict.__init__(self))
        data=json.load(open(input_file))
        for key in data:
            self[key]=data[key]
    def __getattr__(self, item):
        return self[item]

