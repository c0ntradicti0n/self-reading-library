# Distinctiopus4

# Usage

python do/train_multi_corpus.py experiment_configs/elmo_lstm3_feedforward4_crf_straight_fitter.config 

# Explanation

How to mine distinctions/difference utterances in texts? Something like: There are birds, that can fly, and there are penguines, were dodos and some other birds, that can't fly.
This is useful for critics of arguments in a [non-monotonically logical](https://plato.stanford.edu/entries/logic-nonmonotonic/) manner. "Tux is a bird. So he can fly? - Oh, but he is a penguine, so he can't." It's thought to build reasoning machine like H2G2.

Publication is comming.

Here you find the code to build a appropriate AI-model with AllenNLP, to get these utterances out of prose text.

## Getting Started

### Prerequisites and Installing


Get the things:

```
git clone https://github.com/c0ntradicti0n/Distinctiopus4.git
pip install -r requirements.txt
```

There is a corpus and allen-ai-code as well as a definition of a model, that can be trained. The models achieve maximally, 0.90 F1 Score

Train this model:

```
./do/train_difference.sh experiment_configs/elmo_nym_lstm3_feedforward4_crf_straight.config
```

To make some predictions call this script:

```buildoutcfg

```

## Explanation

Essentially its an architecture with bidirectional stacked LSTMs, a feedforward network and a Conditional Ramdom Field, that marks trained passages in the texts.
This architecture is similar to solutions for named entity recognition, because this tasks of marking some spans denoted by semantical informations is very similar.
The only difference is, that a feedforward network is useful to capture more logical information about the constellation of annotations. The corpus-data is in CONLL 2003 format:

```
In  IN  O  O
other  JJ  O  O
words  NNS  O  O
,  PCT  O  O
we  PRP  B-PRP  B-CONTRAST
usually  RB  I-RB  I-CONTRAST
associate  VBP  I-VBP  I-CONTRAST
cool  JJ  I-JJ  I-SUBJECT
with  IN  I-IN  I-CONTRAST
refreshing  VBG  I-VBG  I-CONTRAST
and  CC  I-CC  I-CONTRAST
comfortable  VB  I-VB  I-CONTRAST
lower  JJR  I-JJR  I-CONTRAST
temperature  NN  I-NN  I-CONTRAST
and  CC  O  O
cold  JJ  B-JJ  B-SUBJECT
with  IN  I-IN  I-CONTRAST
uncomfortably  RB  I-RB  I-CONTRAST
lower  JJR  I-JJR  I-CONTRAST
temperature  NN  I-NN  I-CONTRAST
.  PCT  O  O
```

This data is fed into the model. In the mass of these samples negative sampling and "first"-sampling are used for better structuring the predictions of the model, there can be text before and after such samples. It's useful for going step by through documents.


## Built With

* [AllenNlp and Elmo](https://github.com/allenai/allennlp) - The nlp-ai-framework used
* [ampligraph/Accenture](https://github.com/Accenture/AmpliGraph/tree/master/ampligraph) - Knowledge Embeddings (coming?)
* [http://www.differencebetween.net](http://www.differencebetween.net) - Getting Text Samples

## Contributing

Just ask me over some channel on github to speak about something or make your branch. My git behavior may look chaotic, but it's because I'm alone.
If you want to build a machine with ability to do inductive and non-monotonically logical reasoning, feel encouraged to contact me. 

## Versioning

4rth trial to get something fine working.

## Authors

* **Stefan Werner**

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
