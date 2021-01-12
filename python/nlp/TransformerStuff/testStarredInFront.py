from python.layouteagle.StandardConverter.Wordi2Css import Wordi2Css
from python.layouteagle.pathant.PathAnt import PathAnt
from python.nlp.TransformerStuff.ElmoDifference import ElmoDifference
from python.nlp.TransformerStuff.UnPager import UnPager

a = Wordi2Css
b = ElmoDifference
c = UnPager


ant = PathAnt()
ant.info("front_star.png")
pipe = ant("wordi.difference", "css.difference")
vals = [2,3,4]
css_value, html_meta = list(
                    zip(
                        *list(
                            pipe
                            ([(val, {})
                              for val
                              in vals]))))