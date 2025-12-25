import pandas as pd
import plotly.graph_objects as go

def code_mapping(df, src, targ):
    """
    Assign unique integer codes to categorical labels.

    Parameters:
        df (pd.DataFrame): Dataframe containing source and target columns.
        src (str): Source column name.
        targ (str): Target column name.

    Returns:
        pd.DataFrame: Updated dataframe with numerical encoding.
        list: List of labels corresponding to the encoded values.
    """
    labels = list(set(df[src]).union(set(df[targ])))
    lc_map = {label: i for i, label in enumerate(labels)}
    df = df.replace({src: lc_map, targ: lc_map})
    return df, labels

def make_sankey(df, *cols, vals=None):
    """
    Generate a multi-layered Sankey diagram using the given columns.

    Parameters:
        df (pd.DataFrame): The dataset containing categorical relationships.
        *cols (str): Columns to use as layers in the Sankey diagram.
        vals (str): Column name representing numerical values (default: None).

    Returns:
        go.Figure: A Plotly Sankey diagram.
    """

    if len(cols) < 2:
        raise ValueError("Two categorical columns are required for a Sankey diagram.")

    data_frames = []
    for i in range(len(cols) - 1):
        src_col, targ_col = cols[i], cols[i + 1]
        temp_df = df[[src_col, targ_col, vals]].rename(
            columns={src_col: "Source", targ_col: "Target", vals: "Values"}
        )
        data_frames.append(temp_df)

    sankey_data = pd.concat(data_frames)
    sankey_data = sankey_data.groupby(["Source", "Target"], as_index=False).sum()
    sankey_data, labels = code_mapping(sankey_data, "Source", "Target")

    fig = go.Figure(go.Sankey(
        node=dict(label=labels, pad=15, thickness=20),
        link=dict(
            source=sankey_data["Source"],
            target=sankey_data["Target"],
            value=sankey_data["Values"]
        )
    ))

    return fig
