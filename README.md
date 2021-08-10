# TODO

- cache from glob
- think about useful features (dpi, angle, pic?)
- check prediction


# Layout Eagle

This contains some NLP-Pipeline for Layout recognition, semantic analysis, text to speech tool. 

* It's mainly a framework to connect different tools
* It has a deep learning approach to learn layout structures (arbitrarily configurable by learning from tags, that are automaticallyh inserted into LateX files, that are compiled and used for learning layout analysis)
* It employs Elmo (A transformer model like Bert or GPT3 from AllenNLP) to predict semantic tags within the texts
* It brings a dynamic frontend, that hosts pages for backend components. The frontend services and page-components are dynamically built by a backend side configuration
* It shows a Java "Bean" like concept of building dynamic pipelines. The approach is registering all components of the programm as nodes in a directed graph, as "converters" between input and output descriptions. To call the components we use "pipelines", that are dynamically built by asking the graph for the shortest connections. And from these pipelines we get callables, that call all the graphnodes needed for producing the output in a row.




![alt text](https://github.com/c0ntradicti0n/LayoutEagle/blob/master/python/pathant.png?raw=true)


![alt text](https://github.com/c0ntradicti0n/LayoutEagle/blob/master/accuracy_epochs.png?raw=true)

