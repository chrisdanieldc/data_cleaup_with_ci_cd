"""
Drop Duplicates Operation
Removes duplicate rows from the dataset
"""

import pandas as pd


def execute(df, parameters):
    """
    Remove duplicate rows from DataFrame

    Parameters:
        subset: List of columns to check for duplicates (None = all columns)
        keep: Which duplicate to keep ('first', 'last', or False to drop all)

    Returns:
        DataFrame with duplicates removed
    """
    subset = parameters.get("subset")
    keep = parameters.get("keep", "first")

    rows_before = len(df)
    df = df.drop_duplicates(subset=subset, keep=keep)
    rows_after = len(df)

    print(f"  Removed {rows_before - rows_after} duplicate row(s)")

    return df
