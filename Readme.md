# Geodict: an integrated gazetteer

Geodict is a gazetteer built using an extraction process over different datasets in the LOD: Geonames, Wikidata, OpenStreeMap.
The latest version of Geodict contains approximatively 2.8 millions of spatial entity.

## Requirements
  * Python 3.x
  * ~ 10Go of free space on your disk
  * Wikidata last dump in *.gz format
  
## Get the latest version of Geodict

You can directly get **Geodict** by downloading the file [here](http://dx.doi.org/10.18167/DVN1/MWQQOQ)
 
## Create the gazeteer
First, you need to get the latest dump of Wikidata [here](https://dumps.wikimedia.org/wikidatawiki/entities/)
Then, store it wherever you want and indicate its absolute path inside the configuration file (*config/configuration.json*)

Simply run the command line

    $ python3 gazeteer.py
    
## Store the data in a Elasticsearch server

    $ python3 gazeteer2es.py [ES host if not localhost]
    

**Gaurav Shrivastava, Jacques Fize @ 2017**