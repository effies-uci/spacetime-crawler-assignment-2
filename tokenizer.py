from pathlib import Path
from errors import TokenizerException

stops = []

def parse(filepath:Path)->list:
    tokens = []
    currentString = ""
    with (open(filepath, 'r', encoding="UTF-8", errors="strict")) as file:
        while(True):
            thisChar = file.read(1)
            if (not thisChar):
                break
            if (thisChar.isalnum()):
                currentString = currentString + thisChar
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

def removeStops(tokens:list) -> list:
    out = []
    for token in tokens:
        if not isStopWord(token):
            out.append(token)
    return out

def isStopWord(token:str) -> bool:
    if token in stops:
        return True
    else:
        return False
    
def computeWordFrequencies(tokens:list)->dict:
    tokenFrequencies = {}
    for token in tokens:
        if (token in tokenFrequencies.keys()):
            tokenFrequencies[token] += 1
        else:
            tokenFrequencies[token] = 1
    return tokenFrequencies