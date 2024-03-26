import pandas as pd
from typing import List, Optional
from sklearn.preprocessing import OneHotEncoder, LabelEncoder


def one_hot_encode_columns(data_frame: pd.DataFrame, columns_to_encode: Optional[List[str]] = None, exclude_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Applies one-hot encoding to specified columns in the DataFrame, excluding key columns.

    :param data_frame: pandas DataFrame containing the data.
    :param columns_to_encode: Optional list of column names to encode. If None, automatically detects object and category dtype columns.
    :param exclude_columns: Columns to exclude from encoding.

    :return: DataFrame with specified columns one-hot encoded, excluding specified key columns.
    """
    if exclude_columns is None:
        exclude_columns = []

    if columns_to_encode is None:
        columns_to_encode = [col for col in data_frame.select_dtypes(include=['object', 'category']).columns.tolist() if col not in exclude_columns]
    else:
        columns_to_encode = [col for col in columns_to_encode if col not in exclude_columns]

    encoder = OneHotEncoder(sparse=False, handle_unknown='ignore')
    encoded_array = encoder.fit_transform(data_frame[columns_to_encode])
    encoded_df = pd.DataFrame(encoded_array, columns=encoder.get_feature_names_out(columns_to_encode))

    data_frame = data_frame.drop(columns=columns_to_encode).reset_index(drop=True)
    encoded_df = encoded_df.reset_index(drop=True)
    return pd.concat([data_frame, encoded_df], axis=1)


def label_encode_columns(data_frame: pd.DataFrame, columns_to_encode: Optional[List[str]] = None, exclude_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Applies label encoding to specified columns in the DataFrame, excluding key columns.

    :param data_frame: pandas DataFrame containing the data.
    :param columns_to_encode: Optional list of column names to encode. If None, automatically detects object and category dtype columns.
    :param exclude_columns: Columns to exclude from encoding.

    :return: DataFrame with specified columns label encoded, excluding specified key columns.
    """
    if exclude_columns is None:
        exclude_columns = []

    if columns_to_encode is None:
        columns_to_encode = [col for col in data_frame.select_dtypes(include=['object', 'category']).columns.tolist() if col not in exclude_columns]
    else:
        columns_to_encode = [col for col in columns_to_encode if col not in exclude_columns]

    label_encoder = LabelEncoder()
    for column in columns_to_encode:
        data_frame[column] = label_encoder.fit_transform(data_frame[column])

    return data_frame
