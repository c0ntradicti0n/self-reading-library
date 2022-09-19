import logging

import numpy
import pandas


def unpack_list_column(column_name, df, prefix="", suffix=""):
    if not prefix and not suffix:
        raise ValueError("Either prefix or suffix must be given")
    lists = list(df[column_name])
    new_col_names = []
    for i, column_values in enumerate(list):
        new_col_name = prefix + "_" + str(i) + "_" + column_name + suffix
        new_col_names.append(new_col_name)
        df[new_col_name] = column_values
        df[new_col_name] = df[new_col_name].astype(numpy.float16)

    return new_col_names


def load_pandas_file(feature_path):
    try:
        return pandas.read_pickle(feature_path)
    except:
        logging.warning("Could not read pandas pickle!")
        return None
