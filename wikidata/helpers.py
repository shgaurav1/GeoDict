# -*- coding: utf-8 -*-
from collections import defaultdict
from .property_wd import *
from .types_wd import *
import pandas as pd
import json
import sys
import numpy as np
import urllib.request

def getOfficial_label(entity, entry, labels_dict):
    """
    Return official label contains in Geonames

    :param entity:
    :param entry:
    :param labels_dict:
    :return:
    """
    instance_of_geoname = Property("P1566", True, String())
    official_label = ''
    if instance_of_geoname.exists(entry):
        geoID = instance_of_geoname.extractData(entry)
        # print(geoID)
        if geoID[0] in labels_dict:
            official_label = labels_dict[geoID[0]]
    return official_label


def assign_label(lang, official_label, entity, entry):
    if lang in entry['labels'].keys():
        entity[lang] = entry['labels'][lang]['value']
        if official_label == '':
            return entry['labels'][lang]['value']
    else:
        entity[lang] = official_label
    return official_label

def setlabels(entity, entry, labels_list,lang_list):
    official_label = getOfficial_label(entity, entry, labels_list)
    i = 2
    while i>0:
        for l in lang_list:
            official_label = assign_label(l, official_label, entity, entry)
        i-=1



def columns_extract(text):
    columns = text[0]
    text.remove(columns)
    return pd.DataFrame(text, columns=columns)


def read_Tsv(filename,encoding='ascii'):
    f = open(filename,encoding=encoding)
    text = f.read()
    f.close()
    text = text.strip("\n").split('\n')
    for line in range(len(text)):
        text[line] = text[line].split('\t')
    column = text[0]
    del text[0]
    return pd.DataFrame(text,columns = column)
#finding the missing link for wikipedia pages for which wikidata_IDs are not available
def finding_links(files):
    missing_uri=[]
    iterations=0
    total=len(files)
    for file_name in files:
        f = open(file_name,encoding = 'utf-8')
        dataframe = json.load(f)
        f.close()
        try:
           if 'wikidata' in dataframe['properties']['tags']:
               pass
           else:
               if 'wikipedia' in dataframe['properties']['tags']:
                   missing_uri.append(dataframe['properties']['tags']['wikipedia'])
        except Exception as e:
           pass
        iterations = iterations + 1
        if iterations%100 ==0:
           sys.stdout.write("\r Line {0}/{1}".format(iterations,total))
    return missing_uri


def columns_extract(text):
    columns = text[0]
    text.remove(columns)
    return pd.DataFrame(text,columns = columns)


def read_tsv(filename,encoding='ascii',columns = False):
    f = open(filename,encoding = encoding)
    text = f.read()
    f.close()
    text = text.split('\n')
    for line in range(len(text)):
        text[line] = text[line].split('\t')
    if columns:
        return columns_extract(text)
    else:
        return text


def getWikiDataID(dataframe,dic):
    try:
        if 'wikipedia' in dataframe['properties']['tags']:
            title = dataframe['properties']['tags']['wikipedia']
            if title in dic:
                return dic[title]

    except Exception as e:
        pass
    return None
