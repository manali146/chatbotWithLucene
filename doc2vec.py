from __future__ import division, unicode_literals 
import pandas as pd
import nltk
import gensim
import gensim.downloader as api
from gensim.test.utils import datapath
from gensim import corpora
from pprint import pprint
from nltk.tokenize import word_tokenize
import re
import smart_open
import codecs
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from os import listdir
from os.path import isfile, join
import collections
import random

with open('C:\\Personal\\OVGU\\WiSe2020\\IR\\eclipse\\Lucene\\corpusVectors.csv') as f:
    print(f)

#Graph of genre distribution of books
df = pd.read_csv('C:\\Personal\\OVGU\\WiSe2020\\IR\\eclipse\\Lucene\\corpusVectors.csv', header=0, encoding= 'cp1252', delimiter=';')
df.dropna()
df.set_index('id')
print(df)
#print(df['guten_genre'].unique())
print(df['docContent'].value_counts().plot(kind= "bar"))
#plt.show()
#print(df.loc[2,'book_id':'guten_genre'])
#df = pd.read_csv('C:/Personal/OVGU/SoSe2020/ATiML/Project/Gutenberg_English_Fiction_1k/master996.csv',encoding= 'unicode_escape',delimiter=';')                

# model= gensim.models.Word2Vec(abc.sents())
# X= list(model.wv.vocab)
# data=model.most_similar('science')
# print(data)

fname = 'C:\\Personal\\OVGU\\WiSe2020\\IR\\eclipse\\Lucene\\corpusVectors.csv'

import smart_open

def read_corpus(fname, tokens_only=False):
    with smart_open.open(fname, encoding="iso-8859-1") as f:
        for i, line in enumerate(f):
            tokens = gensim.utils.simple_preprocess(line)
            if tokens_only:
                yield tokens
            else:
                # For training data, add tags
                yield gensim.models.doc2vec.TaggedDocument(tokens, [i])


train_corpus = list(read_corpus(fname))

###############################################################################
# Let's take a look at the training corpus
#
print(train_corpus[:2])


import os,glob
#Creating tagged documents from directory of documents
def tag_document(noOfSamples, tokens_only=False):
    folder_path = 'C:\\Personal\\OVGU\\WiSe2020\\IR\\P06\\DatasetP06'
    for filename in glob.glob(os.path.join(folder_path, '*.txt')):
        with open(filename, 'r') as f:
            text = f.read()
            docwords = gensim.utils.simple_preprocess(text)
            yield gensim.models.doc2vec.TaggedDocument(docwords, filename)

noOfTrainSamples = 700
#train_corpus = list(tag_document(noOfTrainSamples))
print(len(train_corpus))

#test_corpus = list(tag_document(noOfTrainSamples, tokens_only=True))
test_corpus = list(tag_document(noOfTrainSamples))

#Train model
model = gensim.models.doc2vec.Doc2Vec(vector_size=50, min_count=2, epochs=10)
model.build_vocab(train_corpus)
model.train(train_corpus, total_examples=model.corpus_count, epochs=model.epochs)

model.save("d2v.model")
model= gensim.models.doc2vec.Doc2Vec.load("d2v.model")

ranks = []
second_ranks = []
for doc_id in range(len(train_corpus)-1):
#for doc_id in range(0,5):
    inferred_vector = model.infer_vector(train_corpus[doc_id].words)
    sims = model.docvecs.most_similar([inferred_vector], topn=len(model.docvecs))
    #print(sims)


# #Similar documents
# print('Document ({})\n'.format(doc_id))
# print(df.loc[doc_id,'docContent'])
# print('Document ({}): «{}»\n'.format(doc_id, ' '.join(train_corpus[doc_id].tags)))
# print(u'SIMILAR/DISSIMILAR DOCS PER MODEL %s:\n' % model)
# for label, index in [('MOST', 0), ('SECOND-MOST', 1), ('MEDIAN', len(sims)//2), ('LEAST', len(sims) - 1)]:
#     print(u'%s %s: \n' % (label, sims[index]))
    #print(u'%s %s: «%s»\n' % (label, sims[index], ' '.join(train_corpus[sims[index][0]].words)))



# Pick a random document from the test corpus and infer a vector from the model
doc_id = random.randint(0, len(test_corpus) - 1)
inferred_vector = model.infer_vector(test_corpus[doc_id].words)
sims = model.docvecs.most_similar([inferred_vector], topn=len(model.docvecs))
print()
# Compare and print the most/median/least similar documents from the train corpus
#print('Test Document ({}): «{}»\n'.format(doc_id, ' '.join(test_corpus[doc_id])))
print('Test Document ({}) : {} \n'.format(doc_id,test_corpus[doc_id].tags))
print(u'SIMILAR/DISSIMILAR DOCS PER MODEL %s:\n' % model)
for label, index in [('MOST', 0)]:
    #print(u'%s %s: «%s»\n' % (label, sims[index], ' '.join(train_corpus[sims[index][0]])))
    print(u'%s %s %s\n' % (label, sims[index], test_corpus[doc_id].tags))


#to find the vector of a document which is not in training data
test_data = word_tokenize("boys".lower())
v1 = model.infer_vector(test_data)
print("V1_infer", v1)

# to find most similar doc using tags
similar_doc = model.docvecs.most_similar([v1])
print("similar doc", similar_doc, test_corpus[doc_id].tags)
print("new similar: ", df.iloc[int(similar_doc[0][0])])



# to find vector of doc in training data using tags or in other words, printing the vector of document at index 1 in training data
#print(model.docvecs['1'])