# coding=utf-8
import sys

class Process(object):
    """
    """
    def __init__(self,id):
        self.id=id

    def processItem(self,entry):
        pass
    def processProperty(self,entry):
        pass

class WDController(object):
    def __init__(self,reader,*args):
        self.reader=reader
        self.process={}
        for arg in args:
            if isinstance(arg,Process):
                self.process[arg.id]=arg

    def process_all(self,v=True):
        iterations = 0
        while self.reader.has_next():
            entry=self.reader.next()
            if entry:
                for id_,proc in self.process.items():
                    if entry["id"][0] == "Q":
                        proc.processItem(entry)
                    else:
                        proc.processProperty(entry)
            iterations+=1

            if iterations%1000 == 0 and v:
            	sys.stdout.write("\rEntity Parsed: "+'{:,}'.format(iterations))
