from core.pathant.PathAnt import PathAnt

ant = PathAnt()
scrape_pipe = ant("arxiv.org", "labeled.pdf")
print (list(scrape_pipe("https://arxiv.org", dont_use_cache=True)))