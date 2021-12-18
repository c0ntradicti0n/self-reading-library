from functools import wraps

from nltk import flatten, OrderedDict
from nltk.corpus.reader import Synset
from nltk.corpus import wordnet

from addict import Dict

def parametrized(dec):
    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)
        return repl
    return layer

wordnet_lookers = {}
@parametrized
def wordnet_looker(fun, kind):
    wordnet_lookers[kind] = fun
    @wraps(fun)
    def aux(*xs, **kws):
        return fun(*xs, **kws)
    return aux

@wordnet_looker('hyponyms')
def get_hyponyms(synset, depth=0, max_depth=1):
    if depth > max_depth:
        return set(synset.hyponyms())
    hyponyms = set()
    for hyponym in synset.hyponyms():
        hyponyms |= set(get_hyponyms(hyponym, depth=depth+1))
    return hyponyms | set(synset.hyponyms())

@wordnet_looker('cohyponyms')
def get_cohyponyms(synset):
    """ Cohyponyms are for exmaple:
    Dog, Fish, Insect, because all are animals, as red and blue, because they are colors.
    """
    cohyponyms = set()
    for hypernym in synset.hypernyms():
        cohyponyms |= set(hypernym.hyponyms())
    return cohyponyms - set([synset])

@wordnet_looker('cohypernyms')
def get_cohypernyms(synset):
    """ Cohypernyms are for exmaple:
    A Legal Document and a Testimony are cohypernyms, because what is a Legal Document is possibly not a Testimony and
    vice versa, but also that may possibly be the case.
    Dog, Fish, Insect are no cohypernyms, because there is no entity, that is at the same time a Dog and a Fisch or an
    Insect.
    """
    cohypernyms = set()
    for hyponym in synset.hyponyms():
        cohypernyms |= set(hyponym.hypernyms())
    return cohypernyms - set([synset])

@wordnet_looker('hypernyms')
def get_hypernyms(synset):
    hypernyms = set()
    for hyponym in synset.hypernyms():
        hypernyms |= set(get_hypernyms(hyponym))
    result_syns = hypernyms | set(synset.hypernyms())
    result = set(flatten([x if isinstance(x, Synset) else x.syn() for x in result_syns]))
    return result


@wordnet_looker('antonyms')
def get_antonyms(synset):
    antonyms = set()
    new_antonyms = set()
    for lemma in synset.lemmas():
        new_antonyms |= set(lemma.antonyms())
        antonyms |= new_antonyms
        for antonym in new_antonyms:
            antonyms |= set(flatten([list(x.lemmas()) for x in antonym.synset().similar_tos()]))
    return antonyms

@wordnet_looker('pertainyms')
def get_pertainyms(synset):
    pertainyms = set()
    new_pertainyms = set()
    for lemma in synset.lemmas():
        new_pertainyms |= set(lemma.pertainyms())
        pertainyms |= new_pertainyms
        for pertainym in new_pertainyms:
            pertainyms |= set(flatten([list(x.pertainyms()) for x in pertainym.synset().similar_tos()]))
    return pertainyms

@wordnet_looker('derivationally_related_forms')
def get_derivationally_related_forms(synset):
    derivationally_related_forms = set()
    new_derivationally_related_forms = set()
    for lemma in synset.lemmas():
        new_derivationally_related_forms |= set(lemma.derivationally_related_forms())
        derivationally_related_forms |= derivationally_related_forms
        for derivationally_related_form in derivationally_related_forms:
            derivationally_related_forms |= set(flatten([list(x.derivationally_related_forms()) for x in derivationally_related_forms.synset().similar_tos()]))
    return derivationally_related_forms

@wordnet_looker('synonyms')
def get_synonyms(synset):
    return synsets()

# derivationally_related_forms and pertainyms definitions

alle = list(wordnet.all_synsets())

def compute_word_net_mapping():
    g = Dict()
    for s in alle:
        object_methods = [method_name for method_name in dir(s)
                          if hasattr(s, method_name) and callable(getattr(s, method_name))]
        for k, om in wordnet_lookers.items():
            try:
                r = list(om(s))
            except TypeError:
                continue
            except AttributeError:
                continue
            if r:
                g[str(s)][k][str(r)]  = 1

#graph = compute_word_net_mapping()
