**System (please complete the following information):**
 - OS: Ubuntu 18.04
 - Python version: 3.7
 - AllenNLP version: 0.9.0
 - PyTorch version: 1.2.0

**Question**
How to map knowledge graph embeddings to allennlp, so that the Viterbi-Algorithm of the crf does not get confused?

I try to use graph embeddings of [Ampligraph](https://github.com/Accenture/AmpliGraph) to map embeddings of a wordnet-graph as embeddings of prose text. I would like to build something similar like this:[Deep Semantic Match Model for Entity Linking Using Knowledge Graph and Text](https://www.sciencedirect.com/science/article/pii/S1877050918302813)

 I have a setting, where I use a LSTM and CRF-Tagger, which works pretty well. And I thought, it would be great, to enrich the probabilistic language models with more declarative knowledge from such graphs as wordnet.
 So I tried to implement this by doing word-sense-disambiguation and lemmatization on the wordnet synsets and retrieving the embeddings of the synset-knowledge-graph as a token-embedder.

 But it comes to problems with the uncontinuous values, I think, that arise from words, that can't be mapped to some embeddings in the graph, as OOV words and stopword-like words, that are left out in wordnet.
 There happen three different things, respectively, what parameters I try with this setting:

 * it seems to predict some tags, that are out of the tags given by the training set
 * the loss function of the crf, which actually can't be negative, runs into negative infinity as it seems
 * the prediction gets stuck at 0.2 F-score (or at 0), that is totally below the values, one can reach without that

The first two errors arise with computations within the crf-tagger.

Do you think, that these graph embeddings are numerically uncompatible with the other embeddings? If there is some embedding for (synset 1)-relation-(synset 2), the comparison of the embeddings of synset1 and 2 should tell the highest probability of the kind of the relation (like synonym, antonym, hypernym, hyperonym). But maybe there underlies some other clustering to this prediction of the relation, so that these embeddings don't express the kind of these relation and the LSTMS I use don't get it?

And regarding those stoppwords and OOV-tokens, that would need some default, could I pad them with some kind of normalization of the embeddings, to not confuse the Viterbi-algorithm?

I prepared a repository, if you want to try something out. (https://github.com/c0ntradicti0n/allennlp_vs_ampligraph)[https://github.com/c0ntradicti0n/allennlp_vs_ampligraph]




