import json
import subprocess
from pprint import pprint

import torch
from _jsonnet import evaluate_file
from allennlp.common.file_utils import cached_path
from allennlp.common.params import parse_overrides, _environment_variables, with_fallback
from python.nlp.TransformerStuff.attentivecrftagger.attentivecrftagger import AttentiveCrfTagger

from python.layouteagle import config
models = ['first'] #, 'over']

import os
import argparse
parser = argparse.ArgumentParser(description='Seq2Seq Tagger')
parser.add_argument('config', type=str, help='input json config to produce multiple models')
args = parser.parse_args()

for model in models:

    tagger_config_file = args.config
    json_override = """' {{"train_data_path": "nlp/TransformerStuff/manual_corpus/train_{model}.conll3",    """ \
                    """  "validation_data_path": "nlp/TransformerStuff/manual_corpus/test_{model}.conll3"}}'"""

    dir, fname = os.path.split(tagger_config_file)
    subprocess.run(["rm", "-rf", config.hidden_folder + '_'.join([model, fname])])

    script = r"""
    allennlp train --include-package nlp.TransformerStuff.attentivecrftagger.attentivecrftagger \
                   {config} \
                   --serialization-dir  {out}/ \
                   -o {json_override}"""  \
        .format(
            json_override=json_override,
            config=tagger_config_file,
            out=config.hidden_folder + '_'.join([model,fname])).format(model=model)
    print (script)
    os.system(script)
