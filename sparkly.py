def display(df, order=None, max_rows=10, max_cols=999):
    ''' Builds a tiny sparkline for every numeric column of a given dataframe and integrates it as part of
    a dataframe column header. Sorry, does not accept Series as the moment!

    :param df: DataFrame object
    :param order: optional ordering scheme for the x-axis (otherwise defaults to the order in the dataframe)
    :param max_rows: max rows displayed to the notebook
    :param max_columns: max columns displayed to the notebook
    :return: an HTML representation of the dataframe
    '''
    # buncha imports
    from IPython.display import HTML
    import numpy as np

    # python object handling doesn't make sense so imma gonna make a copy for now until i get a handle on this
    temp_df = df.copy()
    if order is None:
        order = range(df.shape[0])

    temp_list = []
    # Determines which columns are numeric - changes based on a multilevel column
    if temp_df.columns.nlevels == 1:
        is_num = temp_df.select_dtypes(include=[np.number]).columns.values
    else:
        is_num = temp_df.select_dtypes(include=[np.number]).columns.levels[-1].values

    # iterates through each column and generates a matplotlib chart
    levelcolumn = temp_df.columns.get_level_values(-1)
    for column_name, column_data in zip(levelcolumn, range((len(temp_df.columns)))):
        column = column_name
        if column_name in is_num:
            image = convert_fig(temp_df.iloc[:, column_data].values, order)
            text = column + image
            temp_list.append(text)
        else:
            temp_list.append(column)

    # replace column headers to include html representation of the chart and returns HTML representation
    if temp_df.columns.nlevels == 1:
        temp_df.columns = temp_list
    else:
        # build a column level mapper
        keys = list(levelcolumn)
        values = temp_list
        mapper = dict(zip(keys, values))
        temp_df.rename(columns=mapper, level=-1, inplace=True)
    return HTML(temp_df.to_html(escape=False, max_rows=max_rows, max_cols=max_cols))


def convert_fig(a_series, order):
    ''' Maps a numeric Series as a matplotlib chart and returns a html encoded byte string.

    :param a_series: Series to map
    :order: specified xaxis for ordering
    '''
    import io
    import base64
    import matplotlib.pyplot as plt
    # build tiny chart
    fig = plt.figure()
    fig.set_size_inches(3, .5)
    ax = fig.gca()
    ax.plot(order, a_series)
    ax.axis('off')

    # save png to buffer
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    figdata_png = base64.b64encode(buf.getvalue())
    encode = figdata_png.decode('UTF-8')
    plt.close(fig) # this is to stop images from echoing to ipython
    return '<img src="data:image/png;base64,' + encode + '">'