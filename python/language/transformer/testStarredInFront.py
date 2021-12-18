from core.StandardConverter.Wordi2Css import Wordi2Css
from core.pathant.PathAnt import PathAnt
from language.transformer.ElmoDifference import ElmoDifference
from language.transformer.UnPager import UnPager

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