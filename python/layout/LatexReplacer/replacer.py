from collections import Callable
from typing import Dict, Tuple
from layouteagle.pathant.PathSpec import PathSpec


class SoupReplacer(PathSpec):
    def __init__(self, replacements: Dict[Callable, Tuple[Callable, Callable]], path_spec=None):
        super().__init__()
        self.replacements = replacements
        self.path_spec = path_spec

    def replace_node(self, node, how):
        try:
            self.make_replacement(node.expr, how)

        except:
            raise

    def __call__(self, soup):
        for tag, tex_strings in self.replacements.items():
            for tex_string in tex_strings:

                if tex_string != None:
                        nodes = list(self.find_all(soup, tex_string))
                        nodes = [soup]
                else:
                    try:
                        if not soup.find("document"):
                            nodes = [soup]
                        else:
                            nodes = []
                    except AttributeError:
                        nodes = []

                if not nodes:
                    continue

                for i, node in enumerate(nodes): # plural
                    self.replace_node(node, tag)


import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
