import os
import numpy as np
import pandas as pd
from scipy.stats import zscore
from typing import List, Optional
from sklearn.impute import SimpleImputer


def handle_missing_values(data_frame: pd.DataFrame, imputation_strategy: str = 'mean',
                          constant_fill_value: Optional[float] = None,
                          exclude_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Handles missing values in the DataFrame using specified strategy, excluding specified columns.

    :param data_frame: pandas DataFrame.
    :param imputation_strategy: Strategy for imputation ('mean', 'median', 'most_frequent', or 'constant').
    :param constant_fill_value: Value to use for filling missing values when imputation_strategy='constant'.
    :param exclude_columns: Columns to exclude from imputation.

    :return: DataFrame with missing values handled.
    """
    if exclude_columns is None:
        exclude_columns = []

    numerical_columns = [col for col in data_frame.select_dtypes(include=['float64', 'int64']).columns if
                         col not in exclude_columns]
    categorical_columns = [col for col in data_frame.select_dtypes(include=['object', 'category']).columns if
                           col not in exclude_columns]

    if imputation_strategy == 'constant' and constant_fill_value is not None:
        numerical_imputer = SimpleImputer(strategy=imputation_strategy, fill_value=constant_fill_value)
        categorical_imputer = SimpleImputer(strategy=imputation_strategy, fill_value=constant_fill_value)
    else:
        numerical_imputer = SimpleImputer(strategy=imputation_strategy)
        categorical_imputer = SimpleImputer(strategy='most_frequent')

    data_frame[numerical_columns] = numerical_imputer.fit_transform(data_frame[numerical_columns])
    data_frame[categorical_columns] = categorical_imputer.fit_transform(data_frame[categorical_columns])

    return data_frame


def remove_outliers(data_frame: pd.DataFrame, z_score_threshold: float = 3.0,
                    exclude_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Removes outliers based on the Z-score for numerical columns, excluding specified columns.

    :param data_frame: pandas DataFrame.
    :param z_score_threshold: Z-score value above which data is considered an outlier.
    :param exclude_columns: Columns to exclude from outlier removal.

    :return: DataFrame with outliers removed.
    """
    if exclude_columns is None:
        exclude_columns = []

    numerical_columns = [col for col in data_frame.select_dtypes(include=['float64', 'int64']).columns if
                         col not in exclude_columns]
    df_numerical = data_frame[numerical_columns].apply(zscore)
    mask = (np.abs(df_numerical) < z_score_threshold).all(axis=1)
    data_frame_without_outliers = data_frame[mask]

    return data_frame_without_outliers


def standardize_text_columns(data_frame: pd.DataFrame, columns_to_standardize: Optional[List[str]] = None,
                             exclude_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Standardizes text data to lower case and removes leading/trailing whitespaces, excluding specified columns.

    :param data_frame: pandas DataFrame.
    :param columns_to_standardize: List of column names containing text to be standardized.
    :param exclude_columns: Columns to exclude from text standardization.

    :return: DataFrame with text data standardized.
    """
    if exclude_columns is None:
        exclude_columns = []
    if columns_to_standardize is None:
        columns_to_standardize = []

    columns_to_process = [col for col in columns_to_standardize if
                          col not in exclude_columns and col in data_frame.columns]

    for column_name in columns_to_process:
        data_frame[column_name] = data_frame[column_name].str.lower().str.strip()

    return data_frame


def remove_duplicate_rows(data_frame: pd.DataFrame) -> pd.DataFrame:
    """
    Removes duplicate rows from the DataFrame.

    :param data_frame: pandas DataFrame.

    :return: DataFrame with duplicates removed.
    """
    return data_frame.drop_duplicates()


def clean_dataset(data_frame: pd.DataFrame, key_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Cleans the dataset while ensuring that key columns are not altered.

    :param data_frame: pandas DataFrame to be cleaned.
    :param key_columns: Columns to be excluded from cleaning processes that could alter data.

    :return: Cleaned pandas DataFrame
    """
    if key_columns is None:
        key_columns = []

    data_frame_cleaned = handle_missing_values(data_frame, exclude_columns=key_columns)
    data_frame_cleaned = remove_outliers(data_frame_cleaned, exclude_columns=key_columns)
    columns_to_standardize = [col for col in
                              data_frame_cleaned.select_dtypes(include=['object', 'category']).columns.tolist() if
                              col not in key_columns]
    data_frame_cleaned = standardize_text_columns(data_frame_cleaned, columns_to_standardize=columns_to_standardize,
                                                  exclude_columns=key_columns)
    data_frame_cleaned = remove_duplicate_rows(data_frame_cleaned)

    return data_frame_cleaned
