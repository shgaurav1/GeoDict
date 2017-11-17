import argparse, json, sys
from elasticsearch import Elasticsearch,helpers
from elasticsearch import helpers
import copy

def polygon_transformation4ES(temp,simple=True):
    final = []
    if simple:
        final=copy.copy(temp)
        final.append(temp[0])
        final=final
    else:
        for i in temp:
            t=copy.copy(i)
            t.append(i[0])
            final.append(t)
    return final

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="give input json file")
    parser.add_argument("-e", "--es_host", help="Elasticsearch Host address", default="127.0.0.1")
    args = parser.parse_args()
    file_name = args.input
    es_client = Elasticsearch(args.es_host)
    if not es_client.ping():
        print("Can't connect to ES ! ")
        sys.exit(1)
    if es_client.indices.exists(index="gazetteer"):
        es_client.indices.delete(index="gazetteer")
    gazetteer = open(file_name, encoding='utf-8')
    i = 1
    mappings = json.load(open("config/mappings.json"))
    property_to_be_mapped = json.load(open('config/configuration.json'))
    for prop in property_to_be_mapped["properties_to_extract"]:
        mappings['mappings']['_default_']['properties'][prop['id']] = {'type':prop["mappings"]}
        if prop["mappings_details"]:
            for k,v in prop["mappings_details"].items():
                mappings['mappings']['_default_']['properties'][prop['id']][k]=v
    print(mappings)
    es_client.indices.create(index="gazetteer", body=mappings)
    action_list=[]
    for line in gazetteer:
        data = json.loads(line.strip())
        if '_score' in data.keys():
            data['score'] = data['_score']
            del data['_score']
        if "geometry" in data:
            del data["geometry"]
        if "coord" in data:
            if data["coord"]["lat"] >90 or data["coord"]["lon"] >180:
                i+=1
                continue
        if not data["fr"]:
            i+=1
            continue
                #print("AFTER",data["geometry"])
                #return
        #es_client.index("gazetteer", "place", data)
        actions = {
        "_index": "gazetteer",
        "_type": "place",
        "_source": data
        }
        #print(data["fr"])
        action_list.append(actions)
        if i % 1000 == 0:
            #print(action_list)
            helpers.bulk(es_client,action_list,request_timeout=30)
            sys.stdout.write("\rEntity transferred: " + '{:,}'.format(i))
            action_list = []
        i += 1


if __name__ == '__main__':
    main()
