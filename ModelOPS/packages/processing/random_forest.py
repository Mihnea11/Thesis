import os
import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Optional
from sklearn.ensemble import RandomForestClassifier
matplotlib.use('Agg')


def perform_kruskal_wallis_test(feature_importance_df: pd.DataFrame, p_value_threshold: float = 0.05) -> List[str]:
    """
    Identifies significant features based on their importances using the Kruskal-Wallis H test.

    :param feature_importance_df: A DataFrame with features and their importance scores.
    :param p_value_threshold: The threshold for determining significance, defaults to 0.05.

    :return: A list of significant features.
    """
    median_importance = feature_importance_df['Importance'].median()
    significant_features = feature_importance_df[feature_importance_df['Importance'] > median_importance]['Feature'].tolist()
    return significant_features


def train_random_forest_model(combined_data: pd.DataFrame,
                              target_column: str,
                              max_depth: int,
                              random_state: int,
                              exclude_columns: list) -> pd.DataFrame:
    """
    Trains a RandomForestClassifier on the specified dataset excluding specified features. This function filters out
    non-numeric columns and handles missing values by filling them with the median value of each column.

    :param combined_data: The dataset containing both control and case group data.
    :param target_column: The name of the target variable column.
    :param max_depth: The maximum depth of the trees in the RandomForest, defaults to 5.
    :param random_state: Seed for the random number generator, defaults to 42.
    :param exclude_columns: List of column names to exclude from training.

    :return: A DataFrame containing features and their importance scores. If an error occurs during model fitting,
             an empty DataFrame is returned.
    """
    features = [col for col in combined_data.columns if col not in exclude_columns + [target_column]]
    combined_data[features] = combined_data[features].fillna(combined_data[features].median())

    model = RandomForestClassifier(n_jobs=-1, class_weight='balanced', max_depth=max_depth, random_state=random_state)
    model.fit(combined_data[features], combined_data[target_column])

    importances = model.feature_importances_
    feature_importance_df = pd.DataFrame({'Feature': features, 'Importance': importances})
    return feature_importance_df


def save_results(directory: str, filename: str, data: List[str]) -> None:
    """
    Saves a list of strings to a file in the specified directory.

    :param directory: Directory path where the file will be saved.
    :param filename: Name of the file to create and write to.
    :param data: List of strings to be written to the file.
    """
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, filename)
    with open(file_path, 'w') as file:
        for item in data:
            file.write(f"{item}\n")


def create_box_plots(data: pd.DataFrame, target_column: str, significant_features: List[str], output_dir: str) -> None:
    """
    Creates box plots for each significant feature comparing multiple groups.

    :param data: DataFrame containing the dataset.
    :param target_column: Column name of the target variable.
    :param significant_features: List of significant features to plot.
    :param output_dir: Directory to save the plots.
    """
    plots_dir = os.path.join(output_dir, 'graphics')
    os.makedirs(plots_dir, exist_ok=True)
    for feature in significant_features:
        groups = [group[feature].dropna() for name, group in data.groupby(target_column)]

        plt.figure(figsize=(10, 6))
        plt.boxplot(groups, labels=data[target_column].unique())
        plt.title(f'Box Plot for {feature}')
        plt.ylabel('Value')
        plt.savefig(os.path.join(plots_dir, f'boxplot_{feature}.png'))
        plt.close()


def read_and_process_files(data_dir: str, chunk_size: int = 10000) -> pd.DataFrame:
    """
    Reads CSV files in chunks from a directory and concatenates them into a single DataFrame.

    :param data_dir: Directory containing the CSV files.
    :param chunk_size: Number of rows per chunk to read at a time, defaults to 10000.
    :return: DataFrame containing the concatenated data from all files.
    """
    file_paths = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.csv')]
    chunks = []
    for file_path in file_paths:
        for chunk in pd.read_csv(file_path, chunksize=chunk_size):
            chunks.append(chunk)
    combined_data = pd.concat(chunks, ignore_index=True)
    return combined_data


def run(data_dir: str,
        output_dir: str,
        target_column: str,
        max_depth: int = 5,
        random_state: int = 42,
        chunk_size: int = 10000,
        exclude_columns: Optional[List[str]] = None) -> None:
    """
    Main entry point for running the analysis pipeline. Coordinates data reading, processing, analysis, and result presentation.

    :param data_dir: Directory containing the data files.
    :param output_dir: Directory where all outputs will be saved.
    :param target_column: Column name of the target variable for model training.
    :param exclude_columns: List of column names to exclude from model training.
    :param max_depth: Maximum depth of trees in the RandomForest model.
    :param random_state: Random seed for model reproducibility.
    :param chunk_size: Size of chunks for processing large files.
    """
    print("Starting data processing...")
    combined_data = read_and_process_files(data_dir, chunk_size=chunk_size)
    combined_data = combined_data.dropna(subset=[target_column])
    print("Data loaded and processed.")

    if exclude_columns is None:
        exclude_columns = []

    print("Training RandomForest model on all available features...")
    feature_importances_df = train_random_forest_model(combined_data, target_column, max_depth, random_state, exclude_columns)

    print("Evaluating feature significance...")
    significant_features = perform_kruskal_wallis_test(feature_importances_df)
    print(f"Significant features found: {len(significant_features)}")

    if significant_features:
        print("Saving feature importances...")
        save_results(output_dir, 'feature_importances.txt', [f'{feature}: {imp}' for feature, imp in zip(significant_features, feature_importances_df['Importance'])])

        print("Creating box plots for significant features...")
        create_box_plots(combined_data, target_column, significant_features, output_dir)

    print("Analysis complete. Results and plots are saved.")
