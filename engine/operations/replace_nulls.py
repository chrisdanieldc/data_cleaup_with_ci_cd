"""
Replace Nulls Operation
Replaces null/missing values with specified values
"""

import pandas as pd


def execute(df, parameters):
    """
    Replace null values in specified columns

    Parameters:
        column: Column name to fill (None = all columns)
        fill_value: Value to replace nulls with

    Returns:
        DataFrame with nulls replaced
    """
    column = parameters.get("column")
    fill_value = parameters.get("fill_value", 0)

    if column:
        nulls_count = df[column].isnull().sum()
        df[column] = df[column].fillna(fill_value)
        print(f"  Replaced {nulls_count} null value(s) in '{column}' with '{fill_value}'")
    else:
        nulls_count = df.isnull().sum().sum()
        df = df.fillna(fill_value)
        print(f"  Replaced {nulls_count} null value(s) with '{fill_value}'")

    return df
