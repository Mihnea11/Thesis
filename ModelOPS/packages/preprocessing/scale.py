import pandas as pd
from typing import List, Optional
from sklearn.preprocessing import StandardScaler, MinMaxScaler


def standardize_columns(data_frame: pd.DataFrame, columns_to_scale: Optional[List[str]] = None,
                        exclude_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Standardizes specified numerical columns in the DataFrame to have mean 0 and variance 1, excluding specified columns.

    :param data_frame: pandas DataFrame containing the data.
    :param columns_to_scale: Optional list of numerical column names to standardize. If None, automatically detects float and int dtype columns.
    :param exclude_columns: Columns to exclude from scaling.

    :return: DataFrame with specified columns standardized, excluding specified columns.
    """
    if exclude_columns is None:
        exclude_columns = []

    if columns_to_scale is None:
        columns_to_scale = [col for col in data_frame.select_dtypes(include=['float64', 'int64']).columns.tolist() if
                            col not in exclude_columns]
    else:
        columns_to_scale = [col for col in columns_to_scale if col not in exclude_columns]

    scaler = StandardScaler()
    data_frame[columns_to_scale] = scaler.fit_transform(data_frame[columns_to_scale])

    return data_frame


def min_max_scale_columns(data_frame: pd.DataFrame, columns_to_scale: Optional[List[str]] = None,
                          exclude_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Applies Min-Max scaling to specified numerical columns in the DataFrame to scale them to a given range, typically [0, 1], excluding specified columns.

    :param data_frame: pandas DataFrame containing the data.
    :param columns_to_scale: Optional list of numerical column names to scale. If None, automatically detects float and int dtype columns.
    :param exclude_columns: Columns to exclude from scaling.

    :return: DataFrame with specified columns scaled using Min-Max scaling, excluding specified columns.
    """
    if exclude_columns is None:
        exclude_columns = []

    if columns_to_scale is None:
        columns_to_scale = [col for col in data_frame.select_dtypes(include=['float64', 'int64']).columns.tolist() if
                            col not in exclude_columns]
    else:
        columns_to_scale = [col for col in columns_to_scale if col not in exclude_columns]

    scaler = MinMaxScaler()
    data_frame[columns_to_scale] = scaler.fit_transform(data_frame[columns_to_scale])

    return data_frame
