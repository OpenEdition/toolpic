#!/usr/bin/env python3

__author__ = "morban"
__email__ = "mathieu.orban@openedition.org"

from gensim import models
import matplotlib.pyplot as plt
from wordcloud import WordCloud



lda =  models.LdaModel.load('lda.model')
with open('output_file.txt', 'w') as outfile:
    for i in range(0, lda.num_topics):
        outfile.write('{}\n'.format('Topic #' + str(i + 1) + ': '))
        for word, prob in lda.show_topic(i, topn=20):
            outfile.write('{}\n'.format(word))
        outfile.write('\n')



for t in range(lda.num_topics):
    plt.figure()
    plt.imshow(WordCloud().fit_words({word : prob for word, prob in lda.show_topic(t, topn=20)}))
    plt.axis("off")
    plt.title("Topic #" + str(t+1))
    #plt.show()
    plt.savefig('WorldCloud{}.pdf'.format(str(t+1)), format='pdf')
