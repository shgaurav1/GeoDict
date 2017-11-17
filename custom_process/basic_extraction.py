import json
from gzip import GzipFile
import sys
from collections import defaultdict
import time

from config.configuration import Configuration
from wikidata.helpers import *
from wikidata.types_wd import *
from wikidata.entity_wd import *
from wikidata.property_wd import *
from wikidata.reader import Reader
from wikidata.process_wd import *

config=Configuration("config/configuration.json")
class BasicExtraction(Process):
    def __init__(self, id, labels_fn,page_rank):
        super(BasicExtraction, Process.__init__(self, id))
        self.dataframe = {}
        self.instance_of_prop = Property("P31", True, EntityID())
        self.coord_prop = Property("P625", False, Coordinates())
        self.geoname_prop = Property("P1566", False, ExternalIdentifier())
        self.osm_prop = Property("P402", False, ExternalIdentifier())
        self.loc_prop = Property('P131',True,EntityID())
        self.terrain_prop = Property('P706',True,EntityID())
        self.continent_prop = Property("P30", False, EntityID())
        self.country_prop = Property("P17", False, EntityID())
        self.scores = {}
        print("Loading the geonames labels...")

        f = open(labels_fn, encoding='utf-8')
        self.labels_list = json.load(f)
        f.close()

        f = open(page_rank,encoding = 'utf-8')
        self.scores = json.load(f)
        f.close()

    def processItem(self, entry):
        if self.instance_of_prop.exists(entry):
            if self.geoname_prop.exists(entry) or self.osm_prop.exists(entry) or self.loc_prop.exists(entry) or self.terrain_prop.exists(entry):
                entity = Entity()
                # setting labels
                setlabels(entity, entry, self.labels_list,config.lang_list)
                self.get_alias(entity,entry)
                #print(entity)
                # setting instances
                if self.instance_of_prop.exists(entry):
                    try:
                        entity.instance_of = self.instance_of_prop.extractData(entry)
                    except:
                        print(entry["id"])
                # setting locations
                if self.loc_prop.exists(entry):
                    try:
                        entity['P131'] = self.loc_prop.extractData(entry)
                    except:
                        print(entry["id"])
                if self.terrain_prop.exists(entry):
                    try:
                        entity['P706'] = self.terrain_prop.extractData(entry)
                    except:
                        print(entry["id"])
                if self.coord_prop.exists(entry):
                    entity["coord"] = self.coord_prop.extractData(entry)
                if self.osm_prop.exists(entry):
                    entity["osmID"] = self.osm_prop.extractData(entry)
                if self.geoname_prop.exists(entry):
                    entity["geonameID"] = self.geoname_prop.extractData(entry)
                if self.country_prop.exists(entry):
                    entity["country"] = self.country_prop.extractData(entry)
                if self.continent_prop.exists(entry):
                    entity["continent"] = self.continent_prop.extractData(entry)
                if entry['id'] in self.scores.keys():
                    entity['score'] = self.scores[entry["id"]]
                # setting GeoName ID
                # self.dataframe.append(entity)
                self.dataframe[entry['id']] = entity

    def get_alias(self, entity, entry):
        alias={}
        for lang in config.lang_list:
            alias[lang] = []
            if lang in entry["aliases"]:
                for v in entry["aliases"][lang]:
                    alias[lang].append(v["value"])
        entity["aliases"]=alias





