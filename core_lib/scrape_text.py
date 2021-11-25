import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from bs4 import BeautifulSoup as bs
import string
import os

def get_tag_list(url):
    html_tags = ['h1','h2','h3','p','a','ul','span','input']
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko; Google Web Preview) Chrome/41.0.2272.118 Safari/537.36",
               "Referer":"https://www.google.com"}
    site = requests.get(url,headers=headers)
    soup = bs(site.content,"html.parser")
    tags = soup.find_all(html_tags)
    return [' '.join(s.findAll(text=True)) for s in tags]


def is_all_digits(s):
    for c in s:
        if c.isalpha():
            return False
    return True

def remove_digits(s):
    l = s.split()
    l2 = [word for word in l if not is_all_digits(word)]
    return ' '.join(l2)

def get_top_terms(data,stop_file):
    ngrams = (3,3)
    stops = None
    #stops = ['is','in','and','with','With','or','was','if','the','then','those','them']
    #print(len(stops))
    
    vectorizer = TfidfVectorizer(
           #min_df = 0.35,
           max_df = 0.9,
           ngram_range=ngrams,
           max_features=50,
           #stop_words=stops, 
           lowercase= False)
    vectorizer.fit_transform(data)
    word_to_idf = {  i:j for i,j in zip(vectorizer.get_feature_names() , vectorizer.idf_ ) }
    word_to_idf = sorted(word_to_idf.items() ,key = lambda x : x[1],
                     reverse = False )
    terms = [e[0] for e in word_to_idf]
    return terms

def extract_keywords(url,stop_file):
    tlist = get_tag_list(url)
    tokens = []
    for s in tlist:
        if len(s) > 0:
            #s = remove_stop_words(s,stop_file)
            tokens.append(s)
    tokens2 = []
    for s in tokens:
        if len(s) > 0:
            s = remove_digits(s)
            tokens2.append(s)
    return get_top_terms(tokens2,stop_file)