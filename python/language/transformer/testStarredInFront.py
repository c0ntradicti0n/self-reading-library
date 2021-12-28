from core.StandardConverter.ReadingOrder2Css import ReadingOrder2Css
from core.pathant.PathAnt import PathAnt
from language.transformer.ElmoDifferencePredict import ElmoDifferencePredict
from language.transformer.UnPager import UnPager

a = ReadingOrder2Css
b = ElmoDifferencePredict
c = UnPager


ant = PathAnt()
ant.info("front_star.png")
pipe = ant("reading_order.difference", "css.difference")
vals = [2,3,4]
css_value, html_meta = list(
                    zip(
                        *list(
                            pipe
                            ([(val, {})
                              for val
                              in vals]))))