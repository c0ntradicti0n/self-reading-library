import os
import random
from collections import Counter
from pprint import pprint
import regex as re
from nltk import flatten
from helpers.os_tools import get_files_from_recursive_path
from numpy import cumsum
from argparse import ArgumentParser

parser = ArgumentParser(description='Mixing the corpus to train/test/valid conll3s.')
parser.add_argument('dir',
                    type=str,
                    help='directory to process the files recursively from single commited conll3s',
                    default= "./manually_annotated")
args = parser.parse_args()

def percentage_split(seq, percentages):
    cdf = cumsum(percentages)
    assert cdf[-1] == 1.0
    stops = list(map(int, cdf * len(seq)))
    return [seq[a:b] for a, b in zip([0]+stops, stops)]

conll_line = re.compile(r"([^\s]+)  ([^\s]+)  ([^\s]+)  ([^\s]+)")
conll_line_sanitizer = re.compile(r"([^\s]*)  ([^\s]*)  ([^\s]+)  ([^\s]+)")

allowed =  sorted(""" !?$%&()+,-./0123456789:;?ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]_`abcdefghijklmnopqrstuvwxyz‘’“”""")

def sanitize_conll(path):
    with open(path, 'r+') as f1:
        with open(path[:-1], 'w+') as f2:
            for l in f1.readlines():
                if l:
                    match = conll_line_sanitizer.match(l)
                    if match:
                        token, pos, tag_wod, tag_annot = match.groups()

                        token = "".join([c for c in token if c in allowed])
                        if not token:
                            continue

                        l = "  ".join([token, pos, tag_wod, tag_annot]) + "\n"
                        print (l)
                        f2.write(l)
                    else:
                        f2.write(l)


def read_conll_file (path):
    with open(path, 'r') as f:
        all_lines = f.read()
    splitted = all_lines.split(sep='\n\n')
    random.shuffle(splitted[1:])
    return splitted[1:]

def write_conll_file (path, samples):
    with open(path, 'w+') as f:
        f.write("-DOCSTART- -X- -X- O\n\n")
        f.write("\n\n".join(samples))

set_layout = {'train':0.8,
              'test':0.2}

def zeroize(sample):
    return "\n".join([re.sub(conll_line, r"\1  \2  O  O", line) for line in sample.split('\n')])

def add_only_first_of_pair(samples, how_much):
    pairs = list(zip(samples, samples[1:] + samples[:1]))
    z_pairs = ["\n".join([s,zeroize(z)]) for s,z in pairs]
    return samples + z_pairs[:int(len(z_pairs)*how_much)]

def limit_length(samples):
    return [s for s in samples if len(s.split('\n')) < 210]

models  =  ['first', 'over']
short_dummy = False;
copy = []
if short_dummy:
    set_layout = {'train': 1}
    set_copy = ['train', 'valid', 'test']



def mix_files():
    for model in models:
        path = args.dir + "/topics/**/{model}.conll3"

        print (path.format(model=model))
        relevant_files_paths = list(get_files_from_recursive_path(path.format(model=model)))
        pprint (relevant_files_paths)

        # filtering, changing samples
        all_samples = list(flatten([read_conll_file(path) for path in relevant_files_paths]))
        all_samples = add_only_first_of_pair(all_samples, 0.1)
        all_samples = limit_length(all_samples)
        random.shuffle(all_samples)

        print (model)
        print ("maximal len is %s" % max([len(s.split('\n')) for s in all_samples]))

        # splitting
        tvt = percentage_split(all_samples, list(set_layout.values()))
        names = list(set_layout.keys())
        for name, samples in zip (names, tvt):
            path = args.dir + name + "_" + model +'.conll3x'
            print ("%s-set contains %d samples" %(name, len(samples)) )
            write_conll_file(path, samples)
            sanitize_conll(path)
            os.remove(path)
            if short_dummy:
                for cp in set_copy[1:]:
                    tr_path = args.dir + name + "_" + model + '.conll3'
                    cp_path = args.dir + cp + "_" + model + '.conll3'

                    os.system("cp {path} {cp_path}".format(path=tr_path, cp_path=cp_path))


mix_files()

for model in models:
    with open (args.dir +"train_" + model +".conll3") as f:
        t = f.read()
        all_chars = Counter(t)
        print("".join(sorted(set(all_chars.keys()))))






