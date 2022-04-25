# Layout Eagle

This contains some NLP-Pipeline for Layout recognition, semantic analysis, text to speech tool. 

* It brings a framework to connect a multitude of different tools without spaghetti-code and can be extended
* It has a deep learning approach to learn layout structures (arbitrarily configurable by learning from tags, that are automaticallyh inserted into LateX files, that are compiled and used for learning layout analysis)
* It employs Elmo (A transformer model like Bert or GPT3 from AllenNLP) to predict semantic tags within the texts
* It brings a dynamic frontend, that hosts pages for backend components. The frontend services and page-components are dynamically built by a backend side configuration
* It shows a Java "Bean" like concept of building dynamic pipelines. The approach is registering all components of the programm as nodes in a directed graph, as "converters" between input and output descriptions. To call the components we use "pipelines", that are dynamically built by asking the graph for the shortest connections. And from these pipelines we get callables, that call all the graph nodes represending the processing steps needed for producing the output. The longer the pipelines become, the more we save the spaghetti code, that could be produced by connecting these processing tools and they are reusable.

![internal pipeline workflow (created dynamically)](https://github.com/c0ntradicti0n/LayoutEagle/blob/master/python/workflow.png?raw=true)


# Predicting layout of pdf-papers with or without column layout

![predicted layout sections](https://github.com/c0ntradicti0n/LayoutEagle/documentation/layout-presentation/pics/equation-breaking-all-cols.png?raw=true)

![alt text](https://github.com/c0ntradicti0n/LayoutEagle/blob/master/accuracy_epochs.png?raw=true)


# Semantic search in scientific text for utterances expressing "differences"

Based on a philosophical we try to mine "utterances expressing differences", when different theories, parts of things, meanings, values are compared to each other, as they are the main factor to convey knowledge to the reader, building the structure of decisions the reader may come to after reading.

We have had three trials on this:

1. An algorithm that compares and matches based on antonyms (coming from wordnet) and negations. The comparison is done on all sentences and phrases on a text, that are matched, if the comparisons and antonyms come felicitous together.
2. An algorithm, that uses a fine-tuned transformer-model (based on AllenAI transformer model ELMO), to match phrases that are similar to our handmade corpus
3. An algorithm processing the text peaces with Open-AIs GPT3, that pushes the scientific text into GPT3 with the question "What differences are expressed in this text?"


# Combining the findings of "difference"-sentences

# Topic modelling

