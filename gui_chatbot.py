import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np
import gensim
import pandas as pd


from colorama import Fore
from IPython.display import clear_output
from IPython.display import display
from ipywidgets import Output
import stop_words as stopwords
from stop_words import get_stop_words
import networkx as nx
from nltk.cluster.util import cosine_distance


from keras.models import load_model
doc2vec_model= gensim.models.doc2vec.Doc2Vec.load("d2v.model")
model = load_model('chatbot_model.h5')

import json
import random
intents = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))


def clean_up_sentence(sentence):
    # tokenize the pattern - splitting words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stemming every word - reducing to base form
    #sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


# return bag of words array: 0 or 1 for words that exist in sentence
def bag_of_words(sentence, words, show_details=True):
    # tokenizing patterns
    sentence_words = clean_up_sentence(sentence)
    # bag of words - vocabulary matrix
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,word in enumerate(words):
            if word == s: 
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % word)
    return(np.array(bag))

def predict_class(sentence):
    # filter below  threshold predictions
    p = bag_of_words(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.75
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sorting strength probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    print(tag)
    list_of_intents = intents_json['intents']
    print(list_of_intents)
    for i in list_of_intents:
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            break

    return result

def generate_summary(file_name, top_n=5):
    stop_words = stopwords.get_stop_words('english')
    summarize_text = []

    # Step 1 - Read text anc split it
    sentences =  read_article(file_name)

    # Step 2 - Generate Similary Martix across sentences
    sentence_similarity_martix = build_similarity_matrix(sentences, stop_words)

    # Step 3 - Rank sentences in similarity martix
    sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_martix)
    scores = nx.pagerank(sentence_similarity_graph)

    # Step 4 - Sort the rank and pick top sentences
    ranked_sentence = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)    
    print("Indexes of top ranked_sentence order are ", ranked_sentence)    

    for i in range(len(ranked_sentence)):
        if i<=5:
            summarize_text.append(" ".join(ranked_sentence[i][1]))

    # Step 5 - Ofcourse, output the summarize texr
    print("Summarize Text: \n", ". ".join(summarize_text))
    return summarize_text


def read_article(file_name):
    file = open(file_name, "r")
    filedata = file.readlines()
    article = filedata[0].split(". ")
    sentences = []

    for sentence in article:
        print(sentence)
        sentences.append(sentence.replace("[^a-zA-Z]", " ").split(" "))
    #sentences.pop()
    print(len(sentences))
    
    return sentences
    

def sentence_similarity(sent1, sent2, stopwords=None):
    if stopwords is None:
        stopwords = []
 
    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]
 
    all_words = list(set(sent1 + sent2))
 
    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)
 
    # build the vector for the first sentence
    for w in sent1:
        if w in stopwords:
            continue
        vector1[all_words.index(w)] += 1
 
    # build the vector for the second sentence
    for w in sent2:
        if w in stopwords:
            continue
        vector2[all_words.index(w)] += 1
 
    return 1 - cosine_distance(vector1, vector2)
 
def build_similarity_matrix(sentences, stop_words):
    # Create an empty similarity matrix
    similarity_matrix = np.zeros((len(sentences), len(sentences)))
 
    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1 == idx2: #ignore if both are same sentences
                continue 
            similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2], stop_words)

    return similarity_matrix


def doc2vec_chatbot(sentence):
    quit=False
    responses = []
    
    while quit == False:
        text = sentence
        if text == 'quit()':
            quit=True
        else:
            tokens = text.split()
            ##infer vector for text the model may not have seen
            new_vector = doc2vec_model.infer_vector(tokens)
            ##find the most similar [i] tags
            index = doc2vec_model.docvecs.most_similar([new_vector], topn = 10)

            print('Test Document ({}) : \n'.format(index))
            print(u'SIMILAR/DISSIMILAR DOCS PER MODEL %s:\n' % model)
            #response = Fore.RED + 'Chatbot: ' + train_data.iloc[int(index[0][0])].response
            print(index)

            df = pd.read_csv('C:\\Personal\\OVGU\\WiSe2020\\IR\\eclipse\\Lucene\\corpusVectors.csv',encoding= 'cp1252',delimiter=';')
            print(df.loc[index[0][0]])
            path = df.loc[index[0][0],'docPath']
            print(path)
            summ = generate_summary(path, 2)
            print(type(summ))
            content = df.loc[index[0][0],'docContent']
            response = str(summ)+ '\n\n' + 'Best file: ' + path 
            responses.append(response)
            return response

import os.path, subprocess
from subprocess import STDOUT, PIPE

def compile_java (java_file):
    subprocess.check_call(['javac', java_file])

def execute_java (java_file):
    cmd=['java', java_file]
    proc=subprocess.Popen(cmd, stdout = PIPE, stderr = STDOUT)
    input = subprocess.Popen(cmd, stdin = PIPE)
    print(proc.stdout.read())



#Creating tkinter GUI
import tkinter
from tkinter import *

def send():

    msg = EntryBox.get("1.0",'end-1c').strip()
    EntryBox.delete("0.0",END)

    if msg != '':
        ChatBox.config(state=NORMAL)
        ChatBox.insert(END, "You: " + msg + '\n\n')
        ChatBox.config(foreground="#446665", font=("Verdana", 12 ))
    
        ints = predict_class(msg)
        print(ints)
        if(ints):
            res = getResponse(ints, intents)
        else:
            res = 'This is something I got..' + doc2vec_chatbot(msg)

        ChatBox.insert(END, "Bot: " + res + '\n' '\n\n')
            
        ChatBox.config(state=DISABLED)
        ChatBox.yview(END)
 

root = Tk()
root.title("Chatbot")
root.geometry("400x500")
root.resizable(width=FALSE, height=FALSE)

#Create Chat window
ChatBox = Text(root, bd=0, bg="white", height="8", width="50", font="Arial",)

ChatBox.config(state=DISABLED)

#Bind scrollbar to Chat window
scrollbar = Scrollbar(root, command=ChatBox.yview, cursor="heart")
ChatBox['yscrollcommand'] = scrollbar.set

#Create Button to send message
SendButton = Button(root, font=("Verdana",12,'bold'), text="Send", width="12", height=5,
                    bd=0, bg="#f9a602", activebackground="#3c9d9b",fg='#000000',
                    command= send )

#Create the box to enter message
EntryBox = Text(root, bd=0, bg="white",width="29", height="5", font="Arial")
#EntryBox.bind("<Return>", send)


#Place all components on the screen
scrollbar.place(x=376,y=6, height=386)
ChatBox.place(x=6,y=6, height=386, width=370)
EntryBox.place(x=128, y=401, height=90, width=265)
SendButton.place(x=6, y=401, height=90)

root.mainloop()
