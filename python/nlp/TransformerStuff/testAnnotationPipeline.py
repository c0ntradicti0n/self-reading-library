from pprint import pprint

from python.layout.LayoutReader.PDF2ETC import PDF2ETC
from python.layouteagle.StandardConverter.Wordi2Css import Wordi2Css
from python.nlp.TransformerStuff.ElmoDifference import ElmoDifference
from python.nlp.TransformerStuff.Pager import Pager
from python.nlp.TransformerStuff.UnPager import UnPager

from python.layouteagle.pathant.PathAnt import PathAnt



ant = PathAnt()
ant.info("testAnnotationPipeline.png")
pipe = ant("pdf", "css.difference")
vals = [('test/small_pdfs//5-Level Paging and 5-Level EPT - Intel - Revision 1.1 (May, 2017).pdf', {})]

css_value, html_meta = list(
                        zip(
                            *list(
                                pipe
                                (vals))))


print ("META")
pprint (html_meta)
print ("VALUE")
print (css_value[0])