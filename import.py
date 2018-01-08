#!/usr/bin/env python3

__author__ ='morban'
__email__ = "mathieu.orban@openedition.org"

import pysolr
import os
import sys
import html
import settings as s

import argparse

# argparse
parser = argparse.ArgumentParser(description='Import data from solr. Written by Mathieu Orban.')
parser.add_argument('-i','--index_list', nargs='+', help='If you want to pass a list of different index of year', default=None)
parser.add_argument('-b','--begin', type=int, help='To give a started year to process')
parser.add_argument('-e','--end', type=int, help='To give a ended year to process')
parser.add_argument('-l','--lang',type=str, help='Langage specified')
parser.add_argument('-q','--query',type=str, help='If you want to specify your own query')
parser.add_argument('-p','--platform', type=str, help='type of platform selected', required=True)
parser.add_argument('-d','--directory', type=str, help='directory where text will be saved', default='./train/')
args = parser.parse_args()



def findNumFound(solr, request, fq=None):
    params = {'rows':0, 'fq':fq}
    results = solr.search(request, **params)
    return results.hits

def importCalenda(year):
    solr = pysolr.Solr(s.url_solr, timeout=20)
    request = 'platformID:{} AND yearFacet:{}'.format(args.platform, year)
    #filter_queries = ['resume_{}:[* TO *]'.format(args.lang)]
    filter_queries = ['autodetect_lang:{}'.format(args.lang)]
    numFound = findNumFound(solr, request, fq=filter_queries)
    print(numFound)
    stop = numFound
    step =100
    # Get results by data bundle
    for i in range(0, stop, step):
        print(i)
        params = {'rows':step, 'start':i, 'sort':'id DESC', 'fq':filter_queries}
        results = solr.search(request, **params)
        print(len(results))
        list_files = saveInputFiles(results, year)

def saveInputFiles(results, year):
    year_directory = '{0}/{1}'.format(args.directory, year)
    if not os.path.exists(year_directory):
        os.makedirs(year_directory)
    for result in results:
        name_id = ''.join((result['id'].replace('http://','').replace('/','_'), '.txt'))
        write_path='{}/{}'.format(year_directory, name_id)
        if not os.path.exists('./{}'.format(write_path)):
            mode = 'a'
        else:
            mode = 'w'
        print('\t Processing %s' % write_path)
        naked_titre = ''
        naked_texte = ''
        #naked_titre = html.unescape(result['naked_titre'])
        if 'naked_texte' in result:
            naked_texte = html.unescape(result['naked_texte'])
        if 'naked_titre' in result:
            naked_titre = html.unescape(result['naked_titre'])
        with open('{}'.format(write_path), mode) as f:
            f.writelines([naked_titre, ' ', naked_texte])

if __name__ == '__main__':
    year_list = args.index_list if args.index_list else list(range(args.begin, args.end))
    for i in year_list:
        year = i.__str__()
        print('Processing year : {}'.format(year))
        importCalenda(year)

