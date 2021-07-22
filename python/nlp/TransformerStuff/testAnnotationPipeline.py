import os
import sys

sys.path.append(os.getcwd() + "/../")

from pprint import pprint

from layout.LayoutReader.PDF2ETC import PDF2ETC
from layouteagle.StandardConverter.Wordi2Css import Wordi2Css
from nlp.TransformerStuff.ElmoDifference import ElmoDifference
from nlp.TransformerStuff.Pager import Pager
from nlp.TransformerStuff.UnPager import UnPager

from layouteagle.pathant.PathAnt import PathAnt



ant = PathAnt()
ant.info("testAnnotationPipeline.png")
pipe = ant("pdf", "css.difference")
vals = [('../test/999695fc76ea4a34855764dc1680ba40ff8c.pdf', {})]

css_value, html_meta = list(
                        zip(
                            *list(
                                pipe
                                (vals))))

