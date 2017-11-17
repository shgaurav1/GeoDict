from elasticsearch import Elasticsearch
import json
from scipy.spatial import ConvexHull

from config.configuration import Configuration
from .collision import collide
__cache = {}
__limit=200
config=Configuration("config/configuration.json")



def parseHull(hull_object,points):
    hull=[]
    for simplex in hull_object.simplices:
        hull.append(points[simplex[0]])
        hull.append(points[simplex[1]])
    return hull

def getConvexHull(id):
    es = Elasticsearch()
    res = es.search("gazetteer", "place",
                    body={"query": {"bool": {"must": [{"term": {"id": id}}], "must_not": [], "should": []}},
                          "from": 0,
                          "size": 50, "sort": [], "aggs": {}})
    if 'path' in res["hits"]["hits"][0]["_source"].keys():
        path = res["hits"]["hits"][0]["_source"]["path"]
        data=json.load(open(config.osm_boundaries_dir + path.replace("osm-boundaries/","").lstrip('.'),encoding = 'utf-8'))
        boundaries=data["geometry"]["coordinates"]
        if data["geometry"]["type"]== "Polygon":
            hull = parseHull(ConvexHull(boundaries[-1]),boundaries[-1])
            return [hull]
        else:
            hull=[]
            for bound in boundaries[-1]:
                hull.append(parseHull(ConvexHull(bound),bound))
            return hull
    return []

def add_cache(id_se,hull):
    global __cache,__limit
    if len(__cache) >__limit:
        __cache={}
    __cache[id_se]=hull


def collisionTwoSEBoundaries(id_SE1,id_SE2):
    global __cache
    if id_SE1 in __cache:
        hull_1=__cache[id_SE1]
    else:
        hull_1 = getConvexHull(id_SE1)
        __cache[id_SE1]=hull_1
        add_cache(id_SE1,hull_1)

    if id_SE2 in __cache:
        hull_2=__cache[id_SE2]
    else:
        hull_2 = getConvexHull(id_SE2)
        add_cache(id_SE2,hull_2)


    for h1 in hull_1:
        for h2 in hull_2:
            if collide(h1,h2)[0]:
                return True
    return False
