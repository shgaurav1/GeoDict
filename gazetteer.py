# coding=utf-8
import os,argparse,zipfile,urllib.request

from config.configuration import Configuration
from wikidata.helpers import *
from custom_process.basic_extraction import *
from custom_process.wiki_links import *
from custom_process.class_extraction import *
from custom_process.property_extract import *
from gis.convex_hull import get_convex_hull

__config=Configuration("config/configuration.json")




def temp(filename):
    return os.path.join(__config.temp_dir,filename)

def import_data():

    """
    Download all the important data sources which will be used in creation of geodict!!

    :param labels: temporary file formed during the process
    :param class_codes: temporary file formed during the process
    :param outfile: final json output file with wikidata id linked to geoname id
    :return: None
    """

    print("Downloading Geonames ...")
    filename=temp("allCountries.zip")
    urllib.request.urlretrieve(
        "http://download.geonames.org/export/dump/allCountries.zip",filename)
    print("Geonames data retrieved !!")
    print("Extracting the geonames data!")
    zip_ref = zipfile.ZipFile(filename, 'r')
    zip_ref.extractall("./{0}".format(__config.temp_dir))
    print("Extracted !")
    print("Extracting labels")
    os.system('cut -f 1,2 {0} > {1}'.format(temp("allCountries.txt"),temp("labels.txt")))
    print("Extracting the class")
    os.system('cut -f 1,7,8 {0} > {1}'.format(temp("allCountries.txt"),temp("class_codes.txt")))
    f = open(temp("labels.txt"), encoding = 'utf-8')
    labels = {}
    for line in f:
        line = line.strip().split("\t")
        labels[line[0]] = line[1]
    f.close()
    open(temp("labels.json"), "w").write(json.dumps(labels))#, ensure_ascii=False))
    os.system('git clone https://github.com/missinglink/osm-boundaries.git')


def basic_gazetteer(outfile):

    """
    Extract the basic properties of spatial entities by harvesting wikidata
    :param labels:
    :param wikidata_dump:
    :param outfile: basic gazetteer harvested from wikidata
    :return:
    """

    if not os.path.isfile(os.path.join(__config.temp_dir,"labels.json")):
        print("Give correct labels file name!!")
        return False
    if not os.path.isfile(__config.wikidata_dump):
        print('Give correct path to wikidata json dump ')
        return False

    proc1 = BasicExtraction(1,os.path.join(__config.temp_dir,"labels.json"),"resources/wd_page_rank.json")
    dump = Reader(__config.wikidata_dump,'utf-8')
    controller = WDController(dump,proc1)
    controller.process_all()
    open(outfile, 'w').write(json.dumps(proc1.dataframe))#,ensure_ascii=False))
    return True


def add_properties(input_gazetteer,output_gazetteer,configuration_file):

    """
    add property/properties to the configuration.json file which are to be extracted from wikidata

    :param input_gazetteer:
    :param configuration_file: information about the properties to be harvested from wikidata
    :param outfile: new Geo_dict with added property/properties
    :return:
    """

    prop_to_extract = json.load(open(configuration_file))
    proc1 = PropertyExtract(6,prop_to_extract,input_gazetteer)
    dump = Reader(__config.wikidata_dump,'utf-8')
    controller = WDController(dump,proc1)
    controller.process_all()
    open(output_gazetteer, 'w').write(json.dumps(proc1.dataframe))#,ensure_ascii=False))
    return True


def extract_classes(gazeteer):
    """
    This function maps classes from geonames to instance of property of wikidata
    :param wikidata_dump:
    :param class_codes:
    :param gazeteer:
    :param outfile: Mapped_classes for wikidata-geonames
    :return:
    """
    if not os.path.isfile(__config.wikidata_dump):
        print('Give correct path to wikidata json dump')
        return None
    proc3 = ClassExtraction(1, os.path.join(__config.temp_dir,"class_codes.txt"), gazeteer)
    dump = Reader(__config.wikidata_dump, 'utf-8')
    controller = WDController(dump, proc3)
    controller.process_all()
    open(temp("class_mapped.json"), "w").write(json.dumps(proc3.getOutput()))


def add_classes(gazeteer,outfile):
    """
    This function adds the classes mapped from geonames-wikidata to the geodict
    :param wikidata_dump:
    :param class_codes:
    :param gazeteer:
    :param outfile: Geo_dict with the list of classes
    :return:
    """
    data = json.load(open(gazeteer, encoding='utf-8'))
    classes = json.load(open(temp("class_mapped.json"), encoding='utf-8'))
    outfile = open(outfile, 'w')
    iterations = 0
    places = 0
    keys = set(data.keys())
    for key in keys:
        iterations = iterations + 1
        temp_ = []
        if 'instance_of' in data[key].keys():
            for instance in data[key]['instance_of']:
                if instance in classes.keys():
                    places = places + 1
                    temp_.append(classes[instance])
            data[key]['class'] = list(set(temp_))

        if iterations % 1000 == 0:
            sys.stdout.write("\rEntity Parsed: " + '{:,}'.format(
                iterations) + " Places Parsed: " + '{:,}'.format(places))
    outfile.write(json.dumps(data))#,ensure_ascii=False))


def extract_missing_WikiIDS(interm_outfile,outfile):
    """
    Linking OSM-Wikidata
    :param wikidata_dump:
    :param interm_outfile:
    :param outfile: wikidata-osm links
    :return:
    """
    if not os.path.isfile(__config.wikidata_dump):
        print('Give correct path to wikidata json dump ""\(-_-)/""')
        return None
    df = read_Tsv(os.path.join(__config.osm_boundaries_dir,'meta.tsv'), encoding = 'utf-8')#C:\\Users\shrivastava\Desktop
    paths = [os.path.join(__config.osm_boundaries_dir,'data',path) for path in df['path']]
    del df
    iterations = 0
    output=open(interm_outfile,"w")
    total=len(paths)
    output.write(json.dumps(finding_links(paths)))#,ensure_ascii=False))
    proc2 = WikipediaURI(2, outfile, interm_outfile)
    dump = Reader(__config.wikidata_dump, 'utf-8')
    controller = WDController(dump, proc2)
    controller.process_all()



def missing_wikidata_IDS(missing_ids):
    """

    :param missing_ids: link file of wikidata-osm
    :param meta: meta.tsv file in osm-boundaries
    :param outfile: meta_all.csv
    :return:
    """
    #read the missing_Wikidata_IDS
    text = open(missing_ids,encoding = 'utf-8')#'./temp/missing_Wikidata_IDS.txt'
    dic = {}
    for line in text:
        line=line.strip().split("\t")
        dic[line[0]] = line[1]
    #reading meta.tsv files
    df = read_tsv(os.path.join(__config.osm_boundaries_dir,'meta.tsv'),encoding = 'utf-8',columns = True)#'./osm-boundaries/meta.tsv'
    wikidata_IDs = []
    paths = [os.path.join(__config.osm_boundaries_dir,'data',path) for path in df['path']]
    iterations = 0
    for path in paths:
        f = open(path,encoding = 'utf-8')
        dataframe = json.load(f)
        f.close()
        if 'properties' in dataframe:
            if 'wikidata' in dataframe['properties']['tags']:
                wikidata_IDs.append(dataframe['properties']['tags']['wikidata'])
            elif 'wikipedia' in dataframe['properties']['tags']:
                wikip=dataframe['properties']['tags']['wikipedia']
                if wikip in dic:
                    wikidata_IDs.append(dic[wikip])
                else:
                    wikidata_IDs.append(None)
            else:
                wikidata_IDs.append(None)
        else:
            wikidata_IDs.append(None)
        if iterations%1000 == 0:
            sys.stdout.write("\r iterations: "+'{:,}'.format(iterations))
        iterations = iterations + 1
    df['Wiki_IDs'] = wikidata_IDs
    df.to_csv(temp('meta_all.csv'),index = False)#'temp/meta_all.csv'

def adding_geometry(infile,out_file,output_final_fn):
    """
    This function adds path variable to our gazetteer
    :param infile:meta_all.csv
    :param temporary_output_fn:
    :param final_output_fn: final Geo_dict Output File
    :return:
    """
    df = pd.read_csv(infile)
    path_association={}
    for i in range(df.shape[0]):
        curr=df.loc[i]
        if not pd.isnull(curr["Wiki_IDs"]):
            path_association[df.loc[i]["Wiki_IDs"]]=df.loc[i]["path"]
    Wiki_IDs = set(list(path_association.keys()))
    data = json.loads(open(out_file).read())
    outfile = open(output_final_fn, 'w')
    iterations = 0
    places = 0
    keys = set(data.keys())
    for key in keys:
        iterations = iterations + 1
        temp= data[key]
        temp["id"]=key
        if key in Wiki_IDs:
            path = __config.osm_boundaries_dir+'/data/{0}'.format(path_association[key])#C:\\Users\shrivastava\Desktop\
            temp['path'] = path
            dataframe = json.load(open(path, encoding='utf-8'))
            if 'geometry' in dataframe.keys():
                places = places + 1
                temp['geometry'] = get_convex_hull(dataframe)
        outfile.write(json.dumps(temp)+"\n")#,ensure_ascii=False
        del data[key]

        if iterations % 100 == 0:
            sys.stdout.write("\rEntity Parsed: " + '{:,}'.format(iterations) + " Places with boundaries parsed: " + '{:,}'.format(places))



def main():
    start=time.time()
    if not os.path.exists(__config.temp_dir):
        os.makedirs(__config.temp_dir)
    # Import the data sources required to be harvested for creation of gazetteer
    print("[1/6] Download required datasets...")
    import_data()

    # Create a first basic gazeteer
    print("[2/6] Building the core gazetteer...")
    basic_gazetteer(temp("1stoutput.json"))

    # Associate geonames classe to the instance_of(P31) values
    print("[3/6] Associate a class to each entry...")
    extract_classes(temp("1stoutput.json"))

    # Add class to each entity
    add_classes(temp("1stoutput.json"),temp("2ndoutput.json"))

    # Extract missing wikidata IDs in the boundary data
    print("[4/6] Find missing WD ids within boundary data...")
    extract_missing_WikiIDS(temp('found_missing_links.json'),temp('missing_Wikidata_IDS.txt'))
    missing_wikidata_IDS(temp('missing_Wikidata_IDS.txt'))

    # Adding properties from configuration_file
    print("[5/6] Add user properties...")
    add_properties(temp("2ndoutput.json"),temp("3rdoutput.json"),'config/configuration.json')

    # Add boundaries in the final data
    print("[6/6] Adding adminstrative boundary/ies...")
    adding_geometry(temp("meta_all.csv"),temp("3rdoutput.json"),'out_final.json')

    print("The gazeteer was created in {0} hours".format(((time.time()-start)/60)/60))


if __name__=="__main__":
    main()
