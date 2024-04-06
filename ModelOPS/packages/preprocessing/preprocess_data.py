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

    merge_files(input_directory, output_directory)

    for filename in os.listdir(output_directory):
        if filename.startswith("merged_"):
            file_path = os.path.join(output_directory, filename)
            df = pd.read_csv(file_path)

            df_cleaned = clean_dataset(df, patient_identifier, row_threshold, column_threshold, exclude_columns)

            if encode_method == 'one_hot':
                df_encoded = one_hot_encode_columns(df_cleaned, exclude_columns=exclude_columns)
            elif encode_method == 'label':
                df_encoded = label_encode_columns(df_cleaned, exclude_columns=exclude_columns)
            elif encode_method == 'none':
                df_encoded = df_cleaned
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

preprocess_files(r'C:\Users\z004nwxe\Desktop\test_files', r'C:\Users\z004nwxe\Desktop\test_result', 'CHR_NO', exclude_columns=['CHR_NO', 'CSTAGE'])