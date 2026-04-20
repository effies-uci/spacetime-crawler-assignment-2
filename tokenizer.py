from pathlib import Path
from nltk.stem import PorterStemmer
from errors import TokenizerException
from stops import STOPS
import string

SEPARATORS = [" ", "/n"]

def parse(filepath:Path)->list:
    tokens = []
    currentString = ""
    with (open(filepath, 'r', encoding="UTF-8", errors="strict")) as file:
        while(True):
            thisChar = file.read(1)
            if (not thisChar):
                break
            elif (thisChar in SEPARATORS):
                currentString = currentString + thisChar
            elif (thisChar in string.punctuation):
                continue
            else:
                tokens.append(currentString)
                currentString = ""
                
    if (currentString!=""):
        tokens.append(currentString)
    for i in range(len(tokens)):
        tokens[i] = tokens[i].lower()
    # except FileNotFoundError:
    #     raise FileNotFoundError()
    # except (UnicodeError,UnicodeDecodeError,UnicodeDecodeError,UnicodeTranslateError) as exc:
    #     raise TokenizerException("Unicode error raised")
    return tokens

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
    for token in tokens:
        token = stemmer.stem(token)
    return tokens