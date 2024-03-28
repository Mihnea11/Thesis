import os
import pandas as pd
from merge import merge_files
from clean import clean_dataset
from typing import List, Optional
from scale import standardize_columns, min_max_scale_columns
from encode import one_hot_encode_columns, label_encode_columns


def preprocess_files(input_directory: str,
                     output_directory: str,
                     patient_identifier: str,
                     encode_method: str = 'one_hot',
                     scale_method: str = 'standardize',
                     row_threshold: float = 0.3,
                     column_threshold: float = 0.5,
                     exclude_columns: Optional[List[str]] = None):
    """
    Orchestrates the entire data preprocessing workflow: merging, cleaning, encoding, and scaling, with an option to exclude specific columns from being altered.
    Processes files by merging similar ones, then cleans, encodes, and scales the merged data, excluding specified columns,
    and finally saves the processed data to an output directory.

    :param input_directory: Directory containing the files to process.
    :param output_directory: Directory where processed files will be saved.
    :param encode_method: Encoding method to apply; 'one_hot' or 'label'. Defaults to 'one_hot'.
    :param scale_method: Scaling method to apply; 'standardize' or 'min_max'. Defaults to 'standardize'.
    :param exclude_columns: Columns to be excluded from being altered during the preprocessing steps.
    """

    merge_files(input_directory, output_directory)

    for filename in os.listdir(output_directory):
        if filename.startswith("merged_"):
            file_path = os.path.join(output_directory, filename)
            df = pd.read_csv(file_path)

            df_cleaned = clean_dataset(df, key_columns=exclude_columns)

            if encode_method == 'one_hot':
                df_encoded = one_hot_encode_columns(df_cleaned, exclude_columns=exclude_columns)
            elif encode_method == 'label':
                df_encoded = label_encode_columns(df_cleaned, exclude_columns=exclude_columns)
            else:
                raise ValueError("Invalid encode_method. Choose 'one_hot' or 'label'.")

            if scale_method == 'standardize':
                df_scaled = standardize_columns(df_encoded, exclude_columns=exclude_columns)
            elif scale_method == 'min_max':
                df_scaled = min_max_scale_columns(df_encoded, exclude_columns=exclude_columns)
            else:
                raise ValueError("Invalid scale_method. Choose 'standardize' or 'min_max'.")

            processed_filename = f"processed_{filename}"
            output_file_path = os.path.join(output_directory, processed_filename)
            df_scaled.to_csv(output_file_path, index=False)
            print(f"Processed and saved: {output_file_path}")

            os.remove(file_path)
            print(f"Deleted merged file: {file_path}")
