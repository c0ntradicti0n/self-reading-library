import os
import sys

from core.layout_eagle import LayoutEagle

sys.path.append(os.getcwd() + "/../")

from core.pathant.PathAnt import PathAnt


ant = PathAnt()../test
ant.info("testAnnotationPipeline.png")
pipe = ant("pdf", "assigned.predicted.feature")
vals = [('../test/999695fc76ea4a34855764dc1680ba40ff8c.pdf', {})]

css_value, html_meta = list(
                        zip(
                            *list(
                                pipe
                                (vals))))
