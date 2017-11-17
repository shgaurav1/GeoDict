# coding=utf-8
from wikidata.process_wd import Process
import json
from wikidata.property_wd import *
from wikidata.types_wd import *

class WikipediaURI(Process):
    """docstring for WikipediaURI."""
    def __init__(self,id, file_name,wiki_uri_file):
        super(WikipediaURI, Process.__init__(self,id))
        self.dataframe = {}
        self.uri_miss = json.load(open(wiki_uri_file,encoding = 'utf-8'))
        self.uri_miss=set(self.uri_miss)
        self.outfile = open(file_name,'w',encoding = 'utf-8')

    def processItem(self,entry):
        siteLinks = entry['sitelinks']
        for link in siteLinks:
            rn = link.rstrip('wiki')+':'+siteLinks[link]['title']
            if rn in self.uri_miss:
                self.outfile.write(rn + "\t" + entry['id']+'\n')
