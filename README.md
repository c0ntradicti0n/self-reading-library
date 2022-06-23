# Self-Reading and teachable Library

**Demo: [Self-reading library](http://141.5.100.77/)**

This contains some NLP-Pipeline-Framework for Layout recognition, semantic  text analysis and text to speech tool for audio-books putting together various tools. 

* It brings a framework to connect a multitude of different tools with less spaghetti-code or sorted spaghettis.

* It has a deep learning approach to learn layout structures (arbitrarily configurable by learning from tags, that are automaticallyh inserted into LateX files, that are compiled and used for learning layout analysis)

* It employs Elmo to predict semantic tags within the texts  (A transformer model like Bert or GPT3 from AllenNLP)

* It creates an interactive 3D-universe of Documentens representing the content of the "library". The documents are automatically clustered and the clusters are titled. 
![Library 3D view (created dynamically)](https://github.com/c0ntradicti0n/LayoutEagle/blob/master/universe.png?raw=true)

* It brings a dynamic frontend, that hosts pages for backend components. The frontend services and page-components are dynamically built by the backend!

![internal pipeline workflow (created dynamically)](https://github.com/c0ntradicti0n/LayoutEagle/blob/master/python/workflow.png?raw=true)


# Predicting layout of pdf-papers with or without column layout

![predicted layout sections](https://github.com/c0ntradicti0n/LayoutEagle/blob/master/documentation/layout-presentation/pics/equation-breaking-all-cols.png?raw=true)

# Semantic search in scientific text for utterances expressing "differences"

Based on a philosophical we try to mine "utterances expressing differences", when different theories, parts of things, meanings, values are compared to each other, as they are the main factor to convey knowledge to the reader, building the structure of decisions the reader may come to after reading.

We have had three trials on this:

1. An algorithm that compares and matches based on antonyms (coming from wordnet) and negations. The comparison is done on all sentences and phrases on a text, that are matched, if the comparisons and antonyms come felicitous together.
2. An algorithm, that uses a fine-tuned transformer-model (based on AllenAI transformer model ELMO), to match phrases that are similar to our handmade corpus
3. An algorithm processing the text peaces with Open-AIs GPT3, that pushes the scientific text into GPT3 with the question "What differences are expressed in this text?"

# Use documents from the web
You can paste url in the frontend and the document will be taken into account by the self-reading library!
You can teach with those documents in three ways:
* Annotate the layout

* Annotate some difference-utterances

* The more documents, the more structured and overview-like will the topics become



# Annotating differences in Documents

coming soon

# Combining the findings of "difference"-sentences
... will come...

# Topic modelling
Embeddings, vector representations of the "meaning" of the word, are clusters with Gaussian Clustering to thematically more or less consitent topics. And those clusters are given titles by some TF-IDF-method. 

![Library 3D view (created dynamically)](https://github.com/c0ntradicti0n/LayoutEagle/blob/master/universe.png?raw=true)

# Audiobooks
Create an audiobook from your favorite scientific paper and share it with the rest of the science world to have some great podcast from the machine!
... will come ...

# Credits
* [vasturiano](https://github.com/vasturiano/react-force-graph)
* [arxive.org](https://github.com/vasturiano/react-force-graph)
* [AllenNLP](https://allenai.org/allennlp)
* [pdf2htmlEX](https://pdf2htmlex.github.io/pdf2htmlEX/)
* [parasail](https://github.com/jeffdaily/parasail)
* [layoutlmv2](https://huggingface.co/docs/transformers/model_doc/layoutlmv2)
* [differencebetween.net](http://www.differencebetween.net/)
* To authors of over 60000 npm packages!
* To authors of 2000 Python packages!
* To nature, god and friends!