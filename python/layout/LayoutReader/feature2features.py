import itertools
import pandas

from python.layouteagle import config
from python.helpers.cache_tools import file_persistent_cached_generator
from python.layouteagle.pathant.Converter import converter
from python.layouteagle.pathant.PathSpec import PathSpec


@converter(["assigned.feature"], "features")
class Feature2Features(PathSpec):
    def __init__(self, *args,  n=50, pandas_path=".layouteagle/labeled_features", **kwargs):
        super().__init__(*args, **kwargs)
        self.pandas_path = pandas_path
        self.n = n

    #@file_persistent_cached_generator(config.cache + 'collected_features.json')
    def __call__(self, feature_dfs_meta,  *args, **kwargs):
        df_paths, meta = zip(*list(itertools.islice(feature_dfs_meta, self.n)))
        try:
            dfs = [pandas.read_pickle(df_path) for df_path in df_paths]
        except FileNotFoundError:
            raise FileNotFoundError(f" df_path from {df_paths} not found")
        df = pandas.concat(dfs)
        df.to_pickle(self.pandas_path)
        yield self.pandas_path, meta