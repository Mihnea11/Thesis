import os
import pandas as pd
from typing import List
from fuzzywuzzy import fuzz


def find_similar_files(file_names: List[str], threshold: int = 85) -> List[List[str]]:
    """
    Finds and groups filenames with similarity above a specified threshold.

    :param file_names: List of filenames to compare.
    :param threshold: Similarity threshold for considering two filenames as a match.

    :return: List of lists, where each sublist contains filenames considered similar.
    """

    similar_groups = []
    while file_names:
        base = file_names.pop(0)
        group = [base]
        for other in file_names[:]:
            if fuzz.ratio(base, other) > threshold:
                group.append(other)
                file_names.remove(other)
        similar_groups.append(group)
    return similar_groups


def merge_files(directory_path: str, save_directory: str, threshold: int = 85):
    """
    Merges files in a directory with similar names based on a specified similarity threshold.
    Merged files are saved to a separate directory.

    :param directory_path: Path to the directory containing the files to merge.
    :param save_directory: Directory where merged files will be saved.
    :param threshold: Similarity threshold for considering filenames as a match.
    """

    file_names = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    similar_groups = find_similar_files(file_names, threshold)

    os.makedirs(save_directory, exist_ok=True)

    for group in similar_groups:
        merged_df = pd.DataFrame()
        for file_name in group:
            df = pd.read_csv(os.path.join(directory_path, file_name))
            merged_df = pd.concat([merged_df, df], ignore_index=True)

        save_path = os.path.join(save_directory, f"merged_{group[0]}")
        merged_df.to_csv(save_path, index=False)

