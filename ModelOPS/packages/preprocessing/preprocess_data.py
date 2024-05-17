import os
import pandas as pd
from typing import List, Optional
from difflib import get_close_matches
from packages.preprocessing.merge import merge_files
from packages.preprocessing.clean import clean_dataset
from packages.preprocessing.scale import standardize_columns, min_max_scale_columns
from packages.preprocessing.encode import one_hot_encode_columns, label_encode_columns


def choose_closest_match(user_input, valid_options, cutoff=0.8):
    """
    Selects the closest match from valid options based on similarity, ignoring case differences.

    Args:
        user_input (str): The user's input string.
        valid_options (list): A list of valid option strings.
        cutoff (float): The minimum similarity ratio to consider a match (scale from 0 to 1).

    Returns:
        str: The closest matching string from valid_options if a good match is found,
             otherwise returns None to indicate no acceptable match was found.
    """

    normalized_input = user_input.lower()
    normalized_options = [option.lower() for option in valid_options]

    matches = get_close_matches(normalized_input, normalized_options, n=1, cutoff=cutoff)
    if matches:
        for option in valid_options:
            if option.lower() == matches[0]:
                return option
    return None


def preprocess_files(input_directory: str,
                     output_directory: str,
                     patient_identifier: str,
                     encode_method: str = 'label',
                     scale_method: str = 'standardize',
                     row_threshold: float = 0.3,
                     column_threshold: float = 0.5,
                     exclude_columns: Optional[List[str]] = None):
    """
    Orchestrates an entire data preprocessing workflow including merging, cleaning, encoding, and scaling of data files.
    This process is designed to prepare datasets for further analysis or machine learning training by performing several key preprocessing steps:
    - Merging: Combines similar files from the input directory into merged files in the output directory.
    - Cleaning: Applies data cleaning operations on the merged files, such as removing rows and columns based on missing value thresholds, removing outliers, standardizing text columns, and removing duplicate rows. The process ensures the preservation of specified columns, including a patient identifier.
    - Encoding: Transforms categorical data into numerical formats using either one-hot encoding or label encoding methods, based on the specified 'encode_method'.
    - Scaling: Normalizes or standardizes numerical features in the data, based on the specified 'scale_method'.

    After processing, the cleaned, encoded, and scaled data is saved to the output directory. Merged files used during processing are removed after their processed versions are saved.

    Parameters:
    - input_directory (str): Directory containing the files to process.
    - output_directory (str): Directory where processed files will be saved.
    - patient_identifier (str): The column name used as a unique identifier for patients. This column is preserved during cleaning.
    - encode_method (str, optional): Specifies the method for encoding categorical variables ('one_hot' or 'label'). Defaults to 'one_hot'.
    - scale_method (str, optional): Specifies the method for scaling numerical variables ('standardize' or 'min_max'). Defaults to 'standardize'.
    - row_threshold (float, optional): The threshold for the proportion of missing values in a row, above which the row is removed. Defaults to 0.3.
    - column_threshold (float, optional): The threshold for the proportion of missing values in a column, above which the column is removed. Defaults to 0.5.
    - exclude_columns (List[str], optional): A list of column names to be excluded from being altered during the preprocessing steps, including the patient identifier.
    """
    valid_encode_methods = ['one_hot_encoding', 'label_encoding', 'none']
    valid_scale_methods = ['standardize', 'min_max']

    chosen_encode_method = choose_closest_match(encode_method, valid_encode_methods)
    chosen_scale_method = choose_closest_match(scale_method, valid_scale_methods)

    if not chosen_encode_method:
        raise ValueError(f"Invalid encode_method '{encode_method}'. Choose from {valid_encode_methods}.")
    if not chosen_scale_method:
        raise ValueError(f"Invalid scale_method '{scale_method}'. Choose from {valid_scale_methods}.")

    merge_files(input_directory, output_directory)

    if exclude_columns is None:
        exclude_columns = []

    if patient_identifier not in exclude_columns:
        exclude_columns.append(patient_identifier)

    for filename in os.listdir(output_directory):
        if filename.startswith("merged_"):
            file_path = os.path.join(output_directory, filename)
            df = pd.read_csv(file_path)

            df_cleaned = clean_dataset(df, patient_identifier, row_threshold, column_threshold, exclude_columns)

            if chosen_encode_method == 'one_hot_encoding':
                df_encoded = one_hot_encode_columns(df_cleaned, exclude_columns=exclude_columns)
            elif chosen_encode_method == 'label_encoding':
                df_encoded = label_encode_columns(df_cleaned, exclude_columns=exclude_columns)
            else:
                df_encoded = df_cleaned

            if chosen_scale_method == 'standardize':
                df_scaled = standardize_columns(df_encoded, exclude_columns=exclude_columns)
            elif chosen_scale_method == 'min_max':
                df_scaled = min_max_scale_columns(df_encoded, exclude_columns=exclude_columns)

            processed_filename = f"processed_{filename}"
            output_file_path = os.path.join(output_directory, processed_filename)
            df_scaled.to_csv(output_file_path, index=False)
            print(f"Processed and saved: {output_file_path}")

            os.remove(file_path)
            print(f"Deleted merged file: {file_path}")
