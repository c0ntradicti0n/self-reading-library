#!/bin/sh



allennlp evaluate --include-package xnym_embeddings.xnym_embeddings --include-package attentivecrftagger.attentivecrftagger --weights-file ./output/experiment_configs/difference_stacked_birectional_lstm$1.config/model_state_epoch_$2.th   ./output/experiment_configs/difference_stacked_birectional_lstm$1.config corpus_data/valid.txt