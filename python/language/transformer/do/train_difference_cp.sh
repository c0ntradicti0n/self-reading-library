#!/bin/sh

rm -r ./$2
allennlp train \
  --include-package language.transformer.attentivecrftagger.attentivecrftagger \
  $1 -s ./$2/
#  --include-package language.transformer.xnym_embeddings.xnym_embeddings \
#  --include-package language.transformer.spacy_embedder.spacy_embedder \
#  --include-package language.transformer.nym_embeddings.nym_embeddings \
#  --include-package language.transformer.nym_embeddings.synset_indexer \

