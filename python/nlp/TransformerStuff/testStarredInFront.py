from layouteagle.StandardConverter.Wordi2Css import Wordi2Css
from layouteagle.pathant.PathAnt import PathAnt
from nlp.TransformerStuff.ElmoDifference import ElmoDifference
from nlp.TransformerStuff.UnPager import UnPager

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