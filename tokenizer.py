from pathlib import Path
from nltk.stem import PorterStemmer
from errors import TokenizerException
from stops import STOPS
from bs4 import BeautifulSoup
import string
import re

SEPARATORS = [' ','\n','\t', '\r', '\v', '\f']

def tokenize_html(html: bytes) -> list[str]:
    """returns tokens from readable html, removing stop words"""

    soup = BeautifulSoup(html, "lxml")
    soup.head.decompose()
    text = soup.get_text()
    tokens = parse(text)
    
    return [t for t in tokens if not isStopWord(t) and len(t) > 1]

def count_words(html) -> int:
    """count total words including stop words"""

    soup = BeautifulSoup(html, "lxml")
    soup.head.decompose()
    text = soup.get_text()

    return len(re.findall(r'[a-zA-Z]+', text))

def parse(html_text: str)->list:
    """parses all text into tokens using whitespace"""
    tokens = []
    current_str = ""
    for chr in html_text:
            if not chr:
                break
            elif chr in SEPARATORS:
                if current_str=="":
                    continue
                tokens.append(current_str)
                current_str = ""
            elif chr in string.punctuation:
                continue
            else:
                current_str = current_str + chr.lower()
                
    if current_str!="":
        tokens.append(current_str)

    return tokens



###########################################################################

def normalizeTokens(tokens:list) -> list:
    out = []
    for token in tokens: #change all tokens to lower case
        out.append(token.lower())
    return out

def removeStops(tokens:list) -> list:
    out = []
    for token in tokens:
        if not isStopWord(token):
            out.append(token)
    return out

def isStopWord(token:str) -> bool:
    if token in STOPS:
        return True
    else:
        return False
    
def stemWords(tokens:list) -> list:
    stemmer = PorterStemmer()
    for i in range(len(tokens)):
        tokens[i] = stemmer.stem(tokens[i])
    return tokens

def get_sim_hash(wordfreq):
    v = [0] * 32

    for key in wordfreq.keys():
        word_hash = hash_token(key)

        for i in range(32):
            bit_mask = 1 << i

            if word_hash & bit_mask:
                v[i] += wordfreq[key]
            else:
                v[i] -= wordfreq[key] 
    
    fingerprint = 0
    for i in range(32):
        if v[i] >= 0:
            fingerprint |= (1 << i)
    
    return format(fingerprint, '032b')

def hash_token(word:str):
    h = 0x811c9dc5
    for char in word:
        h ^= ord(char)
        h = (h * 0x01000193) & 0xFFFFFFFF

    return h
