# Why?

There are many implementations, that try to get text and other data from PDF-files.

This is rather complicated, especially for column layouts, because document layout is very, very, very diverse.

There are rule-based approaches, that make mistakes due to problems, that arise from defining rules for many different layouts.

And there are recommendations for using deep learning and non-free services for this.

# Installation

Clone this repository with git and navigate into the repo.

# Layout recognition on PDF data

To obtain a model, start the pipeline defined in 'make_model,py':
```
make_model,py
```

This will

1. Scrape scientific articles from `arxiv.org`, not the pdf, but the latex archivs and unpack them.
2. Compile the compilable ones and replace in the LaTex files the title, author, text and footnotes with names for labels, we want to see there
3. Compile the manipulated files again, multiple times
