# coding=utf-8
import json
from gzip import GzipFile
import sys
from collections import defaultdict
import time
from wikidata.helpers import *
from wikidata.types_wd import *
from wikidata.entity_wd import *
from wikidata.property_wd import *
from wikidata.reader import Reader
from wikidata.process_wd import *



class PropertyExtract(Process):
    def __init__(self, id, properties, data):
        super(PropertyExtract, Process.__init__(self, id))
        self.dataframe = {}
        #self.extract_prop = Property(prop, istype, String())
        self.properties_to_extract = properties['properties_to_extract']
        self.isType = {
          "EntityID":EntityID(),
          "String":String(),
          "Coordinates":Coordinates(),
          "URL":URL(),
          "Time":Time(),
          "Quantity":Quantity(),
          "ExternalIdentifier":ExternalIdentifier()
        }
        print("Extracting property...")

        f = open(data, encoding='utf-8')
        self.dataframe = json.load(f)
        f.close()

    def processItem(self, entry):
        if entry['id'] in self.dataframe.keys():
            for prop in self.properties_to_extract:
                temp_prop =Property(prop['id'],prop["isMultiple"],self.isType[prop['type']])
                if temp_prop.exists(entry):
                    try:
                        self.dataframe[entry['id']][prop['id']] = temp_prop.extractData(entry)
                    except:
                        print(entry["id"])
