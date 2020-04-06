import logging
from collections import Callable
from types import GeneratorType
from typing import Dict, Tuple

from pipey import Pipeable


class SoupReplacer (Pipeable):
    def __init__(self, what:Dict[Callable, Tuple[Callable, Callable]]):
        self.what = what

    def replace_node(self, node, _with):
        try:
            node.replace_with(_with(node))
        except AttributeError:
            raise
        except TypeError:
            logging.info("{node} not replaced")
        except ValueError:
            logging.info("'{node} not in list'")



    def __call__(self, soup):
        for _what, (_where, _with) in self.what.items():
            element_s = _what(soup)
            if not element_s:
                continue
            if not isinstance(element_s, GeneratorType):
                self.replace_node(element_s, _with)
            else:
                for i, element in enumerate(element_s):
                    self.replace_node(element, _with)


import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
