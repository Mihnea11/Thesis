import os
import numpy as np
import pandas as pd
from scipy.stats import zscore
from typing import List, Optional
from sklearn.impute import SimpleImputer


def remove_data_based_on_threshold(data_frame: pd.DataFrame,
                                   patient_identifier: str,
                                   row_threshold: float = 0.3,
                                   column_threshold: float = 0.5,
                                   exclude_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Removes rows and columns based on the specified missing value thresholds,
    while preserving the patient identifier column and any other specified columns.

    :param data_frame: pandas DataFrame to be cleaned.
    :param patient_identifier: Column name for the patient identifier that must not be altered or removed.
    :param row_threshold: Proportion threshold for missing values in rows to be removed.
    :param column_threshold: Proportion threshold for missing values in columns to be removed.
    :param exclude_columns: Columns to be excluded from being removed.
    :return: pandas DataFrame after removing rows and columns based on the specified thresholds.
    """
    try:
        if exclude_columns is None:
            exclude_columns = []
        if patient_identifier not in exclude_columns:
            exclude_columns.append(patient_identifier)

        col_missing_proportion = data_frame.isnull().mean()
        columns_to_drop = col_missing_proportion[
            (col_missing_proportion > column_threshold) & (~col_missing_proportion.index.isin(exclude_columns))].index
        data_frame = data_frame.drop(columns=columns_to_drop)

        row_missing_proportion = data_frame.isnull().mean(axis=1)
        rows_to_drop = row_missing_proportion[row_missing_proportion > row_threshold].index
        data_frame = data_frame.drop(index=rows_to_drop)
    except Exception as e:
        print(f"Error in remove_data_based_on_threshold: {e}")
    return data_frame


def remove_outliers(data_frame: pd.DataFrame,
                    z_score_threshold: float = 3.0,
                    exclude_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Removes outliers based on the Z-score for numerical columns, excluding specified columns.

    :param data_frame: pandas DataFrame.
    :param z_score_threshold: Z-score value above which data is considered an outlier.
    :param exclude_columns: Columns to exclude from outlier removal.

    :return: DataFrame with outliers removed.
    """
    try:
        if exclude_columns is None:
            exclude_columns = []

        numerical_columns = [col for col in data_frame.select_dtypes(include=['float64', 'int64']).columns if
                             col not in exclude_columns]
        if len(numerical_columns) == 0:
            return data_frame

        df_numerical = data_frame[numerical_columns].apply(zscore)
        mask = (np.abs(df_numerical) < z_score_threshold).all(axis=1)
        data_frame = data_frame[mask]
    except Exception as e:
        print(f"Error in remove_outliers: {e}")
    return data_frame


def standardize_text_columns(data_frame: pd.DataFrame, columns_to_standardize: Optional[List[str]] = None,
                             exclude_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Standardizes text data to lower case and removes leading/trailing whitespaces, excluding specified columns.

    :param data_frame: pandas DataFrame.
    :param columns_to_standardize: List of column names containing text to be standardized.
    :param exclude_columns: Columns to exclude from text standardization.

    :return: DataFrame with text data standardized.
    """
    try:
        if exclude_columns is None:
            exclude_columns = []
        if columns_to_standardize is None:
            columns_to_standardize = []

        columns_to_process = [col for col in columns_to_standardize if
                              col not in exclude_columns and col in data_frame.columns]
        for column_name in columns_to_process:
            data_frame[column_name] = data_frame[column_name].str.lower().str.strip()
    except Exception as e:
        print(f"Error in standardize_text_columns: {e}")
    return data_frame


def remove_duplicate_rows(data_frame: pd.DataFrame) -> pd.DataFrame:
    """
    Removes duplicate rows from the DataFrame.

    :param data_frame: pandas DataFrame.

    :return: DataFrame with duplicates removed.
    """
    try:
        data_frame = data_frame.drop_duplicates()
    except Exception as e:
        print(f"Error in remove_duplicate_rows: {e}")
    return data_frame


def clean_dataset(data_frame: pd.DataFrame,
                  patient_identifier: str,
                  row_threshold: float,
                  column_threshold: float,
                  key_columns) -> pd.DataFrame:
    """
    Cleans the dataset by performing several preprocessing steps:
    1. Removes rows and columns based on specified missing value thresholds, while preserving specified columns.
    2. Removes outliers based on the Z-score for numerical columns, excluding specified columns.
    3. Standardizes text columns to lower case and trims leading/trailing whitespaces, excluding specified columns.
    4. Removes duplicate rows from the DataFrame.

    This process ensures that the dataset is cleaned thoroughly while preserving the integrity of key columns, such as patient identifiers.

    :param data_frame: The pandas DataFrame to be cleaned.
    :param patient_identifier: The column name for the patient identifier that must not be altered or removed.
    :param row_threshold: The proportion threshold for missing values in rows to be removed. Rows with a higher proportion of missing values are dropped.
    :param column_threshold: The proportion threshold for missing values in columns to be removed. Columns with a higher proportion of missing values are dropped.
    :param key_columns: A list of columns to be excluded from being altered during the cleaning process, including from outlier removal, text standardization, and the missing value threshold checks. The patient identifier column is automatically preserved.
    :return: A cleaned pandas DataFrame.
    """
    if key_columns is None:
        key_columns = []

    data_frame_cleaned = remove_data_based_on_threshold(data_frame, patient_identifier, row_threshold, column_threshold, key_columns)
    data_frame_cleaned = remove_outliers(data_frame_cleaned, exclude_columns=key_columns)
    data_frame_cleaned = standardize_text_columns(data_frame_cleaned, columns_to_standardize=None, exclude_columns=key_columns)
    data_frame_cleaned = remove_duplicate_rows(data_frame_cleaned)

    return data_frame_cleaned
