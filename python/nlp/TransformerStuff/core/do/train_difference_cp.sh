rm -r ./output/$1
allennlp train --include-package xnym_embeddings.xnym_embeddings \
               --include-package spacy_embedder.spacy_embedder \
               --include-package attentivecrftagger.attentivecrftagger \
                              --include-package nym_embeddings.nym_embeddings \
                              --include-package nym_embeddings.synset_indexer \
               $1 -s ./output/$1/

