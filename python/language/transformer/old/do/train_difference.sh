rm -r ./output/$1
allennlp train --include-package xnym_embeddings.xnym_embeddings \
               --include-package spacy_embedder.spacy_embedder \
               --include-package attentivecrftagger.attentivecrftagger \
               $1 -s ./output/$1/

