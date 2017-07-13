#!/usr/bin/env python3
from gensim.matutils import Sparse2Corpus
import time
import random
from gensim import models
import numpy as np
import csv

## @brief Class design to fit paramaters for lda
class Searcher(object):
    grid = list()
    
    # @brief Instantiate a Searcher object
    # @param ntopics :list. A list of different number of topics
    # @param params:list . A list of alpha parmaeters
    # @corpus :list A list which represente a vectorize document
    # @id2word: dict. A mapping between id and word
    def __init__(self, ntopics, params, corpus, id2word):
        self.ntopics=ntopics
        self.params=params
        self.corpus=corpus
        self.id2word=id2word

    # @brief Split corpus in train and test
    # @return Tuple. A tuple of 2 corpus
    def shuffleCorpus(self):
        cp = list(self.corpus)
        random.shuffle(cp)
        # split into 80% training and 20% test sets
        p = int(len(cp) * .95)
        return (cp[0:p], cp[p:])

    # @brief Display on a csv file the log perplixity for each parameter given
    def search(self):
        (cp_train, cp_test) = self.shuffleCorpus()
        number_of_words = sum(cnt for document in cp_test for _, cnt in document)
        grid = list()
        print('\t\tNumber of words in test corpus: %f\n' % number_of_words)
        for num_topic in self.ntopics:
            for param in self.params:
                print("\t\t**********************************\n \tStarting pass for %d topics and  parameter_value = %.2f\n" % (num_topic, param))
                start_time = time.time()
                lda = models.LdaMulticore(corpus=cp_train, id2word=self.id2word, num_topics=num_topic, chunksize=2000, passes=1, alpha=param, eta=param)
                train_time = time.time() - start_time
                print('\tiTraining time: %s\n' % train_time)
                
                start_time = time.time()
                perplex = lda.bound(cp_test)
                print('\tPerplexity: %4f\n' % perplex)
                
                #per_word_perplex = np.exp2(-perplex / number_of_words)
                per_word_perplex = lda.log_perplexity(cp_test)
                print('\tPer-word Perplexity: %s\n' % per_word_perplex)
                
                elapsed = time.time() - start_time
                print('\tPerplixity time: %s\n' % elapsed)

                result = [num_topic, param, perplex, per_word_perplex, elapsed]
                grid.append(result)
       
        with open('fit_result.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(('topics', 'parameter', 'perplexity', 'per_word-perplexity', 'time'))
            writer.writerows(grid)
            print('\tResult is saved in fit_result.csv\n')
