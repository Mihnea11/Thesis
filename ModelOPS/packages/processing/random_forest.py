import os
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
from typing import List, Optional
from sklearn.ensemble import RandomForestClassifier

import matplotlib
matplotlib.use('Agg')


def perform_kruskal_wallis_test(data: pd.DataFrame, target_column: str, p_value_threshold: float = 0.05) -> List[str]:
    """
    Performs the Kruskal-Wallis test to determine if there are statistically significant differences
    between the distributions of each numerical feature across the categories defined by the target column.

    Parameters:
        data (pd.DataFrame): The dataset containing both features and the target column.
        target_column (str): The name of the target variable column in the dataset.
        p_value_threshold (float): The significance level used to determine feature importance.

    Returns:
        List[str]: A list of significant features based on the Kruskal-Wallis test.
    """
    significant_features = []
    for feature in data.columns:
        if feature == target_column or data[feature].dtype == 'object':
            continue
        grouped_data = [group.dropna() for _, group in data.groupby(target_column)[feature]]
        if len(grouped_data) > 1:
            stat, p_value = stats.kruskal(*grouped_data)
            if p_value < p_value_threshold:
                significant_features.append(feature)
    return significant_features


def train_random_forest_model(combined_data: pd.DataFrame, target_column: str, features: List[str],
                              max_depth: int, random_state: int) -> pd.DataFrame:
    """
    Trains a RandomForestClassifier using specified features and returns feature importances.

    Parameters:
        combined_data (pd.DataFrame): The dataset to train the model on.
        target_column (str): The name of the target variable column.
        features (List[str]): The list of feature names to be used in the model.
        max_depth (int): The maximum depth of the trees in the model.
        random_state (int): Seed for the random number generator to ensure reproducibility.

    Returns:
        pd.DataFrame: A DataFrame containing each feature's name and its importance.
    """
    model = RandomForestClassifier(n_jobs=-1, class_weight='balanced', max_depth=max_depth, random_state=random_state)
    model.fit(combined_data[features], combined_data[target_column])
    importances = model.feature_importances_
    return pd.DataFrame({'Feature': features, 'Importance': importances})


def save_results(directory: str, filename: str, data: pd.DataFrame) -> None:
    """
    Saves the DataFrame to a CSV file in the specified directory.

    Parameters:
        directory (str): The directory path where the file will be saved.
        filename (str): The name of the file to create and write to.
        data (pd.DataFrame): The DataFrame to be written to the file.
    """
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, filename)
    data.to_csv(file_path, index=False)


def create_box_plots(data: pd.DataFrame, target_column: str, features: List[str], output_dir: str) -> None:
    """
    Creates and saves box plots for each significant feature against the target variable.

    Parameters:
        data (pd.DataFrame): The dataset containing the features and target.
        target_column (str): The target variable column name.
        features (List[str]): List of significant features to plot.
        output_dir (str): Directory where the plots will be saved.
    """
    plots_dir = os.path.join(output_dir, 'graphics')
    os.makedirs(plots_dir, exist_ok=True)
    for feature in features:
        plt.figure(figsize=(10, 6))
        data.boxplot(column=[feature], by=target_column)
        plt.title(f'Box Plot for {feature}')
        plt.suptitle('')
        plt.ylabel('Value')
        plt.savefig(os.path.join(plots_dir, f'boxplot_{feature}.png'))
        plt.close()


def run(data_dir: str, output_dir: str, target_column: str, max_depth: int = 5, random_state: int = 42,
        p_value_threshold: float = 0.05) -> None:
    """
    Main function to execute the feature selection and model training pipeline.

    Parameters:
        data_dir (str): The directory containing the data files.
        output_dir (str): The directory where all outputs will be saved.
        target_column (str): The name of the target variable for model training.
        max_depth (int): Maximum depth of trees in the RandomForest model.
        random_state (int): Random seed for model reproducibility.
        p_value_threshold (float): Threshold for determining feature significance via Kruskal-Wallis test.
    """
    print("Starting data processing...")
    data_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.csv')]
    data_frames = [pd.read_csv(f) for f in data_files]
    combined_data = pd.concat(data_frames, ignore_index=True)
    combined_data[target_column].fillna(0, inplace=True)
    print("Data loaded and processed.")

    print("Evaluating feature significance using Kruskal-Wallis test...")
    significant_features = perform_kruskal_wallis_test(combined_data, target_column, p_value_threshold)
    print(f"Significant features found: {len(significant_features)} - {significant_features}")

    if significant_features:
        print("Training RandomForest model on significant features only...")
        feature_importances_df = train_random_forest_model(combined_data, target_column, significant_features, max_depth, random_state)
        save_results(output_dir, 'feature_importances.csv', feature_importances_df)
        print("Feature importances saved.")

        print("Creating box plots for significant features...")
        create_box_plots(combined_data, target_column, significant_features, output_dir)
        print("Box plots saved.")

    print("Analysis complete. Results and plots are saved.")
