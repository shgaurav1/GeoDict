# coding=utf-8
from elasticsearch import Elasticsearch
import os,json
from flask import Flask,render_template, make_response ,request, redirect, session, Markup,jsonify
from scipy.spatial import ConvexHull
import numpy as np

osm_boundaries_path='/Users/jacquesfize/install/'

def parseBoundaries(points):
    """
    Transform Boundaries coordinates format
    :param points:
    :return:
    """
    hull=[]
    for p in points:
        hull.append([p[1],p[0]])
    return hull

def getBoundaries(id):
    """
    Return Boundary(ies) data for the spatial entity corresponding to an id
    :param id:
    :return:
    """
    global osm_boundaries_path
    es = Elasticsearch()
    res = es.search("gazetteer", "place",
                    body={"query": {"bool": {"must": [{"term": {"id": id}}], "must_not": [], "should": []}},
                          "from": 0,
                          "size": 50, "sort": [], "aggs": {}})
    if 'path' in res["hits"]["hits"][0]["_source"].keys():
        path = res["hits"]["hits"][0]["_source"]["path"]
        data=json.load(open( osm_boundaries_path + path.lstrip('.'),encoding = 'utf-8'))
        boundaries=data["geometry"]["coordinates"]
        if data["geometry"]["type"]== "Polygon":
            hull = parseBoundaries(boundaries[-1])
            return [hull]
        else:
            hull=[]
            for bound in boundaries[-1]:
                hull.append(parseBoundaries(bound))
            return hull
    return []


app = Flask(__name__)


def get_data(id):
    """
    Return data from Geodict with its id
    :param id:
    :return:
    """
    es = Elasticsearch()
    res = es.search("gazetteer", "place",
                    body={"query": {"bool": {"must": [{"term": {"id": id}}], "must_not": [], "should": []}},
                          "from": 0,
                          "size": 50, "sort": [], "aggs": {}})
    if res["hits"]["total"] > 0:
        res = res["hits"]["hits"][0]["_source"]
    return res

@app.route('/autocomplete',methods=['GET'])
def autocomplete():
    """
    For autocomplete research formular
    :return:
    """
    search = request.args.get('query')
    es=Elasticsearch()
    q={"query":{"bool":{"must":[{"query_string":{"default_field":"_all","query":search}}],"must_not":[],"should":[]}},"from":0,"size":50,"sort":[{"score":"desc"}],"aggs":{}}
    res=es.search("gazetteer","place",body=q)
    print(res)
    fin=[]
    if res["hits"]["total"] >0:
        res=res["hits"]["hits"]
        for r in res:
            fin.append({"data":r["_source"]["id"],"value":r["_source"]["en"]})

    return json.dumps({"suggestions":fin})

@app.route('/')
@app.route('/<idw>')
def index(idw=None):
    """
    Main page
    :param idw:
    :return:
    """
    if idw:
        data=get_data(idw)
    else:
        data=get_data("Q90")
    coord_=None
    poly_=None
    if "coord" in data:
        coord_=[data["coord"]["lat"],data["coord"]["lon"]]
    if "path" in data:
        poly_=getBoundaries(data["id"])
    return render_template('index.html',entry=data,coord=coord_,poly=poly_)

if __name__ == '__main__':
    port = 5000 + 889
    url = "http://127.0.0.1:{0}".format(port)
    app.secret_key=os.urandom(24)
    app.run(host='0.0.0.0',port=port, debug=True)
