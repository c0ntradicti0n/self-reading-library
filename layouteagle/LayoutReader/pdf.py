import logging
from typing import Callable


class Pdf:
    def __init__(self):
        pass

    def verify(self, serious=False, test_document=False, columns=None):
        attributes = {attr: getattr(self,attr)
                      for attr in dir(self)
                      if not isinstance(getattr(self,attr), Callable)
                      and not attr.startswith("__")}

        if test_document:
            score = 0
            for page, cols in self.pages_to_column_to_text.items():
                if columns == self.columns:
                    score += 10
                if len(cols) == self.columns:
                    score += 10
                for i, (col_number, col_text) in enumerate(cols.items()):
                    if "text" in col_text and "column" in col_text:
                        score += 1
                    if str(i + 1) in col_text:
                        score += 3 * col_text.count(str(i + 1))
                        score -= 3 * sum([1, *[col_text.count(str(j + 1)) for j in range(len(cols)) if j != i+1]])

            return score

        for attr, value in attributes.items():
            if not value:
                logging.error(f"{attr} is not set")
                if serious:
                    assert value






    #title = ""
    columns = 0
    #columns_per_page = []
    text = ""
    indexed_words = {}
    #footnotes = []
    #bibliography = []