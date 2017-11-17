# coding=utf-8

import os
import json
import sys
import time
import argparse
import zipfile
import urllib.request
from gzip import GzipFile
from collections import defaultdict
from elasticsearch import Elasticsearch
try:
    from helpers.collision_with_gazetteer_data import *
except Exception as e:
    from gis.collision_with_gazetteer_data import *
import time
import math

a = 1
b = 1
fib_no = []
fib_no.append(0)
fib_no.append(0)
for i in range(30):
    c = a + b
    fib_no.append(c)
    a = b
    b = c

es_client=Elasticsearch()
def get_inclusion_tree(id, prop):
    """
    For an entity return it geographical inclusion tree using a property.
    """
    arr = []
    current_entity = get_data(id)
    while True:
        if prop in current_entity:
            arr.append(current_entity[prop][0])
            current_entity = get_data(current_entity[prop][0])
        else:
            arr.append('Q2')
            break
    return arr


def inclusion_log(x, alpha=0.2):
    return math.log(x)

def get_inclusion_score(id1, id2):  # is it really inclusion ? :)
    list1 = get_inclusion_tree(id1, 'P131')
    list2 = get_inclusion_tree(id2, 'P131')
    interP131 = len(list(set(list1).intersection(list2)))
    list1 = get_inclusion_tree(id1, 'P706')
    list2 = get_inclusion_tree(id2, 'P706')
    interP706 = len(list(set(list1).intersection(list2)))
    #return fib_no[interP131]+fib_no[interP706]
    return inclusion_log(interP131) + inclusion_log(interP706)


def get_data(id):
    es = Elasticsearch()
    res = es.search("gazetteer", "place",
                    body={"query": {"bool": {"must": [{"term": {"id": id}}], "must_not": [], "should": []}},
                          "from": 0,
                          "size": 50, "sort": [], "aggs": {}})
    if res["hits"]["total"] > 0:
        res = res["hits"]["hits"][0]["_source"]
    return res


def label_search(label,lang):

    query = {"query":{"bool":{"must":[{"term":{lang:label}}],"must_not":[],"should":[]}},"size": 50}
    # query = {"query":{"bool":{"must":[{"multi_match" :
    # "fuzzy":{"query":label,"fields": [ "en", "fr"
    # ,"es","de"]}}],"must_not":[],"should":[]}},"from":0,"size":500,"sort":[],"aggs":{}}
    response = es_client.search('gazetteer', 'place', body=query)
    if 'hits' in response['hits']:
        return response['hits']['hits']
    return None


def Adjacency_P47(id1, id2):
    data_1, data_2 = get_data(id1), get_data(id2)
    if "P47" in data_1 and "P47" in data_2:
        if set(data_1["P47"]).intersection(data_2["P47"]):
            return True
    return False


def Adjacency_Hull(id1, id2):
    return collisionTwoSEBoundaries(id1, id2)


def pagerank(entities):
    #disambiguated_entity = {}
    disambiguated = None
    score = 0
    for entry in entities:
        if 'score' in entry:
            if score < float(entry['score']):
                disambiguated = entry
                score = float(entry['score'])
    return disambiguated


def disambiguate(spat_candidates, fixed_entities):
    score_dc = {}

    for cand in spat_candidates:
        id_cand = cand["id"]
        score_dc[id_cand] = 0
        for fixed in fixed_entities:
            id_fixed = fixed_entities[fixed]["id"]
            if Adjacency_P47(id_cand, id_fixed):
                score_dc[id_cand] += 3
            if Adjacency_Hull(id_cand, id_fixed):
                score_dc[id_cand] += 2
            score_dc[id_cand] += get_inclusion_score(id_cand, id_fixed)
    m=max(score_dc, key=score_dc.get)
    if score_dc[m]<4:
        return None
    for cand in spat_candidates:
        if cand["id"] == m:
            return cand


def disambiguate_all(list_of_entities,lang="fr"):
    fixed_entities = {}
    ambiguous_entities = {}
    for entity in list_of_entities:
        request = label_search(entity,lang)
        if len(request) > 1:
            ambiguous_entities[entity] = [r["_source"] for r in request]
        elif len(request) == 1:
            fixed_entities[entity] = request[0]["_source"]

    d_amb_results = {}
    for amb_ent in ambiguous_entities:
        d = disambiguate(ambiguous_entities[amb_ent], fixed_entities)
        if not d:

            d_amb_results[amb_ent] = pagerank(ambiguous_entities[amb_ent])
        else:
            d_amb_results[amb_ent] = d
    for k, v in d_amb_results.items():
        fixed_entities[k] = v
    for k, v in fixed_entities.items():
        fixed_entities[k] = v["id"]
    return fixed_entities


    # Inclusion_country(entity,fixed_entities)
if __name__ == '__main__':
    l = ['Turquie', 'États-Unis', 'Russie',
         'Syrie', 'La Haye', 'Damas', 'Paris', 'Moscou']
    print(json.dumps(disambiguate_all(l), indent=4))
