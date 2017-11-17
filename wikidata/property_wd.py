# coding=utf-8

class Property(object):
    """docstring for property."""
    def __init__(self, id,isMultiple,type_):
        self.id=id
        self.isMultiple=isMultiple
        self.type=type_

    def exists(self,data):
        if 'claims' in data:
            if self.id in data["claims"] and self.type.check_conformity(self.id,data):
                return True
        return False

    def extractData(self,data):
        return self.type.extractData(self.id,self.isMultiple,data)
