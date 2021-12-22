from core.pathant.PathAnt import PathAnt
from language.transformer.ElmoDifferencePredict import ElmoDifferencePredict
from language.transformer.UnPager import UnPager

a = UnPager
b = ElmoDifferencePredict

ant = PathAnt()
ant.info("erase_and_star.png")
pipe = ant("reading_order.page.difference", "reading_order.difference")
vals = [2,3,4]
css_value, html_meta = list(
                    zip(
                        *list(
                            pipe
                            ([(val, {})
                              for val
                              in vals]))))