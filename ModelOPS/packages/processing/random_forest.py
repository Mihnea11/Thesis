import os
import shap
import numpy as np
import pandas as pd
import seaborn as sns
import scipy.stats as stats
from pandas import DataFrame
import matplotlib.pyplot as plt
from typing import List, Optional, Any
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


import matplotlib
matplotlib.use('Agg')


def perform_kruskal_wallis_test(data: pd.DataFrame, target_column: str, p_value_threshold: float = 0.05) -> List[str]:
    """
    Performs the Kruskal-Wallis test to determine if there are statistically significant differences between the distributions of each numerical feature across the categories defined by the target column.

    :param data: The dataset containing both features and the target column.
    :param target_column: The name of the target variable column in the dataset.
    :param p_value_threshold: The significance level used to determine feature importance.

    :return: A list of significant features based on the Kruskal-Wallis test.
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


def train_random_forest_model(combined_data: pd.DataFrame, target_column: str, features: List[str], max_depth: int, random_state: int) -> tuple[DataFrame, RandomForestClassifier, Any]:
    """
    Trains a RandomForestClassifier using specified features, returns feature importances as percentages, and evaluates the model's accuracy on a test set.

    :param combined_data: The dataset to train the model on.
    :param target_column: The name of the target variable column.
    :param features: The list of feature names to be used in the model.
    :param max_depth: The maximum depth of the trees in the model.
    :param random_state: Seed for the random number generator to ensure reproducibility.

    :return: A DataFrame containing each feature's importance as a percentage and the accuracy of the model on the test set.
    """
    train_data, test_data = train_test_split(combined_data, test_size=0.2, random_state=random_state)

    model = RandomForestClassifier(n_jobs=-1, class_weight='balanced', max_depth=max_depth, random_state=random_state)
    model.fit(train_data[features], train_data[target_column])

    importances = model.feature_importances_
    importances_percentage = 100 * importances / importances.sum()
    feature_importances_df = pd.DataFrame({'Feature': features, 'Importance (%)': importances_percentage})

    feature_importances_df = feature_importances_df.sort_values(by='Importance (%)', ascending=False)

    predictions = model.predict(test_data[features])
    accuracy = accuracy_score(test_data[target_column], predictions)

    accuracy = round(accuracy, 2)
    feature_importances_df.loc[len(feature_importances_df)] = ['Accuracy', accuracy * 100]

    return feature_importances_df, model, test_data


def save_results(directory: str, filename: str, data: pd.DataFrame) -> None:
    """
    Saves the DataFrame to a text file in the specified directory with the format Feature:Importance.

    :param directory: The directory path where the file will be saved.
    :param filename: The name of the file to create and write to.
    :param data: The DataFrame to be written to the file.
    """
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, filename)
    with open(file_path, 'w') as file:
        for index, row in data.iterrows():
            file.write(f"{row['Feature']}:{row['Importance (%)']}\n")


def create_box_plots(data: pd.DataFrame, target_column: str, features: List[str], output_dir: str) -> None:
    plots_dir = os.path.join(output_dir, 'graphics')
    os.makedirs(plots_dir, exist_ok=True)

    if not pd.api.types.is_numeric_dtype(data[target_column]):
        data[target_column] = data[target_column].astype(str)

    for feature in features:
        plt.figure(figsize=(12, 8))
        if pd.api.types.is_numeric_dtype(data[feature]):
            sns.boxplot(x=target_column, y=feature, data=data)

            sns.stripplot(x=target_column, y=feature, data=data, color='k', alpha=0.5, size=3)  # Smaller markers

            grouped = data.groupby(target_column)[feature]
            means = grouped.mean()
            stds = grouped.std()
            counts = grouped.count()

            for i, (mean, std, count) in enumerate(zip(means, stds, counts)):
                plt.text(i, data[feature].max(), f'Mean: {mean:.2f}\nSD: {std:.2f}\nCount: {count}',
                         color='red', ha='center', va='top')

            plt.ylabel(f'{feature} Measurement')
        else:
            sns.countplot(x=target_column, hue=feature, data=data)
            plt.ylabel('Count')

        plt.title(f'{feature} by {target_column}')
        plt.xlabel(target_column)
        plt.savefig(os.path.join(plots_dir, f'plot_{feature}.png'))
        plt.close()


def apply_shap_explanations(model, test_data: pd.DataFrame, features: List[str], output_dir: str) -> None:
    """
    Apply SHAP to explain the model's predictions for each class in a multi-class model
    and save the results in separate bar plots for each class.

    :param model: The trained model.
    :param test_data: The dataset containing the features.
    :param features: List of feature names used in the model.
    :param output_dir: Directory where the SHAP plots will be saved.
    """
    output_dir = os.path.join(output_dir, "shap")
    os.makedirs(output_dir, exist_ok=True)

    filtered_test_data = test_data[features]

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(filtered_test_data)

    if isinstance(shap_values, np.ndarray) and len(shap_values.shape) == 3:
        mean_abs_shap_values = np.mean(np.abs(shap_values), axis=(0, 2))

        shap_values_mean = np.mean(shap_values, axis=2)

        plt.figure()
        plt.bar(features, mean_abs_shap_values)
        plt.title('Average Impact of Features Across All Classes')
        plt.xlabel('Features')
        plt.ylabel('Mean Absolute SHAP Value')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'consolidated_shap_summary_plot.png'))
        plt.close()

        shap.summary_plot(shap_values_mean, filtered_test_data, feature_names=features, show=False, plot_size=(20, 15))
        plt.savefig(os.path.join(output_dir, 'shap_summary_dot_plot.png'))
        plt.close()

        shap.summary_plot(shap_values_mean, filtered_test_data, plot_type="bar", feature_names=features, show=False, plot_size=(20, 15))
        plt.savefig(os.path.join(output_dir, 'shap_summary_bar_plot.png'))
        plt.close()

        instance_index = 0
        shap_values_instance = np.mean(shap_values[instance_index, :, :], axis=1)
        shap.force_plot(explainer.expected_value[0], shap_values_instance,
                        features=filtered_test_data.iloc[instance_index, :], show=False, matplotlib=True,
                        figsize=(40, 10))
        plt.savefig(os.path.join(output_dir, 'force_plot_instance.png'))
        plt.close()
    else:
        print("Unexpected structure of SHAP values. Check the SHAP values calculation.")


def run(data_dir: str,
        default_data_path: str,
        output_dir: str,
        target_column: str,
        max_depth: int = 15,
        random_state: int = 42,
        p_value_threshold: float = 0.05,
        excluded_columns: Optional[List[str]] = None) -> None:
    """
    Main function to execute the feature selection, model training, and model evaluation pipeline.

    :param data_dir: The directory containing the data files.
    :param output_dir: The directory where all outputs will be saved.
    :param target_column: The name of the target variable for model training.
    :param max_depth: Maximum depth of trees in the RandomForest model.
    :param random_state: Random seed for model reproducibility.
    :param p_value_threshold: Threshold for determining feature significance via Kruskal-Wallis test.
    :param excluded_columns: Optional list of column names to exclude from processing.
    """
    print("Starting data processing...")
    data_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.csv')]
    default_data_files = [os.path.join(default_data_path, f) for f in os.listdir(default_data_path) if
                          f.endswith('.csv')]
    data_frames = [pd.read_csv(f) for f in data_files]
    default_data_frames = [pd.read_csv(f) for f in default_data_files]

    combined_data = pd.concat(data_frames, ignore_index=True)
    combined_data[target_column].fillna(0, inplace=True)

    default_data = pd.concat(default_data_frames, ignore_index=True)
    default_data[target_column].fillna(0, inplace=True)

    if excluded_columns:
        combined_data = combined_data.drop(columns=excluded_columns, errors='ignore')
        default_data = default_data.drop(columns=excluded_columns, errors='ignore')
    print("Data loaded and processed.")

    print("Evaluating feature significance using Kruskal-Wallis test...")
    if len(combined_data.columns) > 30:
        significant_features = perform_kruskal_wallis_test(combined_data, target_column, p_value_threshold)
    else:
        significant_features = []
        for col in combined_data.columns:
            if col != target_column:
                significant_features.append(col)
    print(f"Significant features found: {len(significant_features)} - {significant_features}")

    if significant_features:
        print("Training RandomForest model on significant features only...")
        feature_importances_df, model, test_data = train_random_forest_model(combined_data, target_column,
                                                                             significant_features, max_depth,
                                                                             random_state)
        save_results(output_dir, 'feature_importances.txt', feature_importances_df)
        print("Feature importances and model accuracy saved.")

        print("Creating box plots for significant features...")
        create_box_plots(default_data, target_column, significant_features, output_dir)
        print("Box plots saved.")

        print("Applying SHAP for model explanation...")
        apply_shap_explanations(model, test_data, significant_features, output_dir)
        print("SHAP explanations saved.")

    print("Analysis complete. Results and plots are saved.")
