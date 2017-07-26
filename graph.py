#!/usr/bin/env python3

__author__ = "morban"
__email__ = "mathieu.orban@openedition.org"

import pandas
import matplotlib.pyplot as plt

df = pandas.read_csv('fit_result.csv')
for i in df['parameter'].unique():
    x = df[df['parameter']==i]['topics']
    y = df[df['parameter']==i]['per_word-perplexity']
    plt.title('Parameter dependency')
    plt.xlabel('Number of Topics')
    #plt.ylim([-1, 20])
    plt.ylabel('Perplexity By word')
    plt.plot(x,y, linestyle='--', marker='o', label='alpha=%s' %i)
    plt.tick_params(axis='y', which='both', labelleft='off', labelright='on')
    plt.legend(loc='best')
plt.savefig('Alpha_correlation.pdf', format='pdf')
plt.close()



for i in df['topics'].unique():
    x = df[df['topics']==i]['parameter']
    y = df[df['topics']==i]['per_word-perplexity']
    plt.title('Topic dependency')
    plt.xlabel('parameter')
    #plt.ylim([-1, 20])
    plt.ylabel('Perplexity By word')
    plt.plot(x,y, linestyle='--', marker='o', label='topic=%s' %i)
    plt.tick_params(axis='y', which='both', labelleft='off', labelright='on')
    plt.legend(loc='best')
plt.savefig('Num_topics_correlation.pdf', format='pdf')

