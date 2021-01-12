import json
from pprint import pprint

from _jsonnet import evaluate_file
from allennlp.common.file_utils import cached_path
from allennlp.common.params import parse_overrides, _environment_variables, with_fallback

models  =  ['first', 'over']

import os
import argparse
parser = argparse.ArgumentParser(description='Videos to images')
parser.add_argument('config', type=str, help='input jason config to produce multiple models')
args = parser.parse_args()

for model in models:
    config = args.config
    json_override = """' {{"train_data_path": "manual_corpus/train_{model}.conll3",    """ \
                    """  "validation_data_path": "manual_corpus/test_{model}.conll3"}}'""" 

    #overrides_dict = parse_overrides(json_override.format(model=model))
    #params_file = cached_path(config)
    #file_dict = json.loads(evaluate_file(params_file))

    #param_dict = with_fallback(preferred=overrides_dict, fallback=file_dict)

    #pprint (param_dict)

    script = r"""
    rm -r ./output/{out}
    allennlp train --include-package xnym_embeddings.xnym_embeddings \
                   --include-package spacy_embedder.spacy_embedder \
                   --include-package attentivecrftagger.attentivecrftagger \
                   {config} \
                   --serialization-dir  ./output/{out}/ \
                   -o {json_override}"""  \
        .format(json_override=json_override, config=config, out='_'.join([model,config])).format(model=model)
    print (script)
    os.system(script)
