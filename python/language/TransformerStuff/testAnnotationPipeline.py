import os
import sys

sys.path.append(os.getcwd() + "/../")

from core.pathant.PathAnt import PathAnt



ant = PathAnt()
ant.info("testAnnotationPipeline.png")
pipe = ant("pdf", "css.difference")
vals = [('../test/999695fc76ea4a34855764dc1680ba40ff8c.pdf', {})]

css_value, html_meta = list(
                        zip(
                            *list(
                                pipe
                                (vals))))

