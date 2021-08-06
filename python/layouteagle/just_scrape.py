from layout.ScienceTexScraper.scrape import ScienceTexScraper
from layout.LatexReplacer.latex_replacer import LatexReplacer
from layouteagle.pathant.PathAnt import PathAnt

ant = PathAnt()
scrape_pipe = ant("arxiv.org", "labeled.pdf")
print (list(scrape_pipe("https://arxiv.org", dont_use_cache=True)))