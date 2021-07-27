def unpack_list_column(column_name, df, prefix='', suffix=''):
    if not prefix and not suffix:
        raise ValueError("Either prefix or suffix must be given")
    lists = list(df[column_name])
    all_column_values = list(zip(*lists))
    new_col_names = []
    for i, column_values in enumerate(all_column_values):
        new_col_name = prefix + "_" + str(i) + "_" + column_name + suffix
        new_col_names.append(new_col_name)
        df[new_col_name] = column_values

    return new_col_names
