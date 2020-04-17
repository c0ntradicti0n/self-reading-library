import logging
import string

import pandas

from pathant.Converter import converter
from pathant.PathSpec import PathSpec


@converter("feature", "features")
class Feature2Features(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, feature_dfs_meta,  *args, **kwargs):
        dfs, meta = list(zip(*list(feature_dfs_meta)))
        df = pandas.concat(dfs)
        try:
            df['chars'] = df.divs.apply(lambda div: sum(div.text.count(c) for c in string.ascii_letters))
            df['nums'] = df.divs.apply(lambda div: sum(div.text.count(c) for c in string.digits))
            df['signs'] = df.divs.apply(lambda div: sum(div.text.count(c) for c in string.punctuation))
            df.divs = df.divs.astype(str)
        except Exception as e:
            logging.error(f"bad content, failed with {e}")
            raise
        df.to_pickle(self.pandas_pickle_path)

        yield self.pandas_pickle_path