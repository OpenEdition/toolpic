#!/usr/bin/env python3

__author__ = "morban"
__email__ = "mathieu.orban@openedition.org"

import os
import sys
from gensim import corpora, models
import logging
import string
import re
import nltk
import multiprocessing
from multiprocessing import Pool
from searcher import Searcher
import argparse


levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]

# argparse
parser = argparse.ArgumentParser(description='Detect topics from a set of documents. One document is one file. One file is one big line. Written by Mathieu Orban.')
parser.add_argument('-s','--stemming', type=bool, help='To stem text before processing', default=False)
parser.add_argument('-l','--lang',type=str, help='Langage specified', default='english')
parser.add_argument('-d','--directory', type=str, help='Set of document directory. (Recurservely loop through directories)', required=True)
parser.add_argument('-f','--fit_params', type=bool, help='If you want to determinate the alpha parmater the most efficient', default=False)
parser.add_argument('-v', '--verbose', action='count', help='Activate verbose mode (more -v == more verbose)', default=0)
parser.add_argument('-b','--base_list', nargs='+', help='A files list which contain different generic list (one word=one line) to get off stop word.', default=['stop_tartarus.txt', 'stop_calenda.txt'])
parser.add_argument('-m','--memory_care', type=bool, help='Call the filter dict function to keep only 100 000. Usefull when number of topics is large. \
                                                    As a reminder, ram uses is  8bytes*num_terms*num_topics. If > 1GB, Multicore is bugging (http://bugs.python.org/issue24550)', default=False)



## @brief Class to extract bag of words
# for memory friendly usage
# @note overload __iter__ builtin function for that
class MyCorpus(object):
    def __init__(self, dictionary):
        self.dictionary = dictionary

    def __iter__(self):
        for line in open('/tmp/gensim_docs.txt'):
           yield self.dictionary.doc2bow(line.lower().split())


## @brief Get several files list of stop word and 
# convert in python list 
#@param stemming bool : if you want to stem word or not
#@return list of word
def stopList(stemming=True):
    stop_list = []
    for stop_file in args.base_list:
        stop_list.extend(getList(stop_file, stemming))
    return stop_list


## @brief Get one file list of stop word and 
# convert in python list 
#@param stop_file str  : file_path
#@param stemming bool : if you want to stem word or not
#@return list of word
def getList(stop_file, stemming=True):
        with open(stop_file, "r") as f:
            stop_list = [ st.rstrip() for st in f.readlines()]
            if stemming:
                return [stemmer.stem(stop_lem) for stop_lem in stop_list]
            else:
                return stop_list


def delShortWord(tokens):
    return [w for w in tokens if len(w)>1]


## @brief delete hours token 
#@param tokens : a list of words
#@return list of word
def delHours(tokens):
    #print('Delete hours')
    regexp = r"(^[0-9]{1,2}[hH]?[0-9]{0,2}\.?$)"
    regex = re.compile(regexp)
    return [w for w in tokens if regex.match(w) is None]


def delPunctuation(txt):
    #print('Delete punctuation for text of lenght: {})'.format(len(txt)))
    remove = string.punctuation
    remove = remove.replace("-", "") # don't remove hyphens
    remove = remove.__add__('’')
    pattern = r"[{}]".format(remove) # create the pattern
    return re.sub(pattern, " ", txt)


def mergeLines(root, file_name):
    #print('Merge Lines')
    with open(os.path.join(root, file_name), 'r') as f:
        text = f.readlines()
        text_list = [t.replace("\n"," ") for t in text]
        return "".join(text_list)


## @brief write a big file.txt where one line is one document.
#  @note This is a native format input for gensim
#  @param dir_doc : str. directory which contain all documents
#  @stemming : Boolean. 
def saveDocs(dir_doc, stemming=True):
    with open('/tmp/gensim_docs.txt', 'w') as f_docs:
        process_limit = int(multiprocessing.cpu_count()*2)
        text_pool = Pool(process_limit)
        for root, dirs, files in os.walk(dir_doc):
            texts = list()
            for name in files:
                text = mergeLines(root, name)
                if text is None:
                    break
                texts.append(text)
            msg = '\tStart to clean %s texts' % len(texts)
            print(msg, flush=True) 
            if stemming:
                print('\tCleaning and stemming Text')
                texts_cleaned = text_pool.map(stemmingText, texts)
            else:
                print('\tCleaning Text')
                texts_cleaned = text_pool.map(cleanText, texts)
            for text_lem in texts_cleaned:
                f_docs.write(text_lem+"\n")
            print('\tText writed in /tmp/gensim_docs.txt', flush=True) 

def cleanToToken(text):
    new_text = delPunctuation(text)
    tokens = nltk.word_tokenize(new_text, args.lang)
    long_tokens = delShortWord(tokens)
    return delHours(long_tokens)

## @brief process text to clean it
#  @param text : str. text to handle. 
#  @return string 
def cleanText(text):
    tokens = cleanToToken(text)
    text_lem = " ".join(tokens)
    return text_lem


## @brief clean text and stem it.
#  @param text : str. text to handle. 
#  @return string 
def stemmingText(text):
    tokens = cleanToToken(text)
    stem = [stemmer.stem(w) for w in tokens]
    text_lem = " ".join(stem)
    return text_lem

## @brief Used gensim library
def gensimProcess(stemming):
    from six import iteritems
    dictionary = corpora.Dictionary(line.lower().split() for line in open('/tmp/gensim_docs.txt'))
    stop_list = stopList(stemming)
    print("\tFilter tokens matching with a stop list and tokens present in all documents")
    stop_ids = [dictionary.token2id[stop_w] for stop_w in stop_list if stop_w in dictionary.token2id]
    once_ids = [tokenid for tokenid, docfreq in iteritems(dictionary.dfs) if docfreq ==1]
    #Filter dictionnary from stop word and token uses only one.
    dictionary.filter_tokens(stop_ids + once_ids)
    if args.memory_care:
        print('filter extremes')
        dictionary.filter_extremes(no_below=8, no_above=0.4, keep_n=80000)
    dictionary.compactify()
    corpus_memory_friendly = MyCorpus(dictionary)
    corpus = list()
    print("\tVectorize with tfidf model")
    tfidf = models.TfidfModel(corpus_memory_friendly)
    for vector in corpus_memory_friendly:
        corpus.append(tfidf[vector])
    #if you want to save corpus
    #corpora.BleiCorpus.serialize('/tmp/corpus.lda-c', corpus)
    #corpus = corpora.BleiCorpus('/tmp/corpus.lda-c')
    if args.fit_params:
        print('\tInstantiate searcher')
        #params_alpha=[0.01, 0.1, 0.25]
        nums_topics=[20, 50, 100, 175, 300, 400, 500]
        params_alpha=[0.01, 0.1, 0.25, 0.5, 0.75, 1.00]
        searcher = Searcher(nums_topics, params_alpha, corpus, dictionary)
        searcher.search()
    else:
        lda = models.LdaMulticore(corpus, id2word=dictionary, num_topics=500, iterations=50, passes=25, alpha=1, eta=0.01)
        lda.save('lda.model')


def setLog():
    level = levels[len(levels)-(args.verbose+1)]
    print(level)
    logging.basicConfig(filename='lda_model.log', format='(%(levelname)s): %(message)s', level=level)
    return logging.getLogger()
    

if __name__ == "__main__":
    args = parser.parse_args()
    stemming = args.stemming
    stemmer = nltk.stem.SnowballStemmer(args.lang)
    log = setLog()
    dir_doc = args.directory
    print('\tProcess Textes')
    saveDocs(dir_doc, stemming)
    gensimProcess(stemming)
