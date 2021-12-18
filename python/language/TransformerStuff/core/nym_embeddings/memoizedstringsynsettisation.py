#import nltk
#nltk.download('wordnet')
# C:\Users\Student\AppData\Roaming\nltk_data
from functools import lru_cache
from pprint import pprint

from nym_embeddings.pywsd.allwords_wsd import disambiguate_tokens
from nym_embeddings.wordnet2relationmapping import *


pprint(wordnet_lookers)


#@lru_cache(maxsize=None)
def lazy_lemmatize_tokens(tokens:tuple):
    return disambiguate_tokens(tokens)


