# coding=utf-8
from wikidata.process_wd import Process
import json
from wikidata.property_wd import *
from wikidata.types_wd import *

class ClassExtraction(Process):
    """docstring for WikipediaURI."""
    def __init__(self,id,classe_code_4all,output_first_pass):
        super(ClassExtraction, Process.__init__(self,id))
        self.geoname_prop=Property("P1566", False, String())
        self.instance_of_prop=Property("P31", True, EntityID())

        self.class_data=self.loadGeoClass(classe_code_4all)
        self.keys=set(json.load(open(output_first_pass)).keys())
        self.places=0
        self.data_count={}

    	#print("LOADED !!")
    def processItem(self,entry):
        if entry['id'] in self.keys:
            if self.geoname_prop.exists(entry) and self.instance_of_prop.exists(entry):
                try:
                    instance_ofs=self.instance_of_prop.extractData(entry)
                except:
                    print(entry["id"])
                    return
                geoID=self.geoname_prop.extractData(entry)
                if geoID in self.class_data:
                    geo_class_code="-".join(self.class_data[geoID])
                    for i in instance_ofs:
                        if not i in self.data_count:self.data_count[i]={}
                        if not geo_class_code in self.data_count[i]:self.data_count[i][geo_class_code]=0
                        self.data_count[i][geo_class_code]+=1
                    self.places+=1
    def loadGeoClass(self,file):
    	f=open(file)
    	data={}
    	for line in f:
    		line=line.strip().split("\t")
    		data[line[0]]=line[1:3]
    	return data
    def getOutput(self):
        final={}
        for d in self.data_count:
            max_key=max(self.data_count[d],key=self.data_count[d].get)
            final[d]=max_key
        return final
