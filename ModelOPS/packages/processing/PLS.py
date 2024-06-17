import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from scipy.stats import spearmanr


def generate_data(num_samples: int = 1000) -> pd.DataFrame:
    data = pd.read_csv(r'D:\Projects\Thesis\ModelOPS\testing\data\t2d_dataset.csv')
    return data


def perform_pca(data: pd.DataFrame, target_column: str, n_components: int = 2) -> pd.DataFrame:
    X = data.drop(columns=[target_column])

    pca = PCA(n_components=n_components)
    pca.fit(X)

    pca_importances = np.abs(pca.components_).sum(axis=0)
    pca_importances_percentage = 100 * pca_importances / pca_importances.sum()

    feature_importances_df = pd.DataFrame({'Feature': X.columns, 'Importance (%)': pca_importances_percentage})
    feature_importances_df = feature_importances_df.sort_values(by='Importance (%)', ascending=False)

    return feature_importances_df


def train_random_forest_model(data: pd.DataFrame, target_column: str, max_depth: int,
                              random_state: int) -> pd.DataFrame:
    features = data.drop(columns=[target_column]).columns.tolist()
    train_data, test_data = train_test_split(data, test_size=0.2, random_state=random_state)

    model = RandomForestClassifier(n_jobs=-1, class_weight='balanced', max_depth=max_depth, random_state=random_state)
    model.fit(train_data[features], train_data[target_column].astype('int'))

    importances = model.feature_importances_
    importances_percentage = 100 * importances / importances.sum()
    feature_importances_df = pd.DataFrame({'Feature': features, 'Importance (%)': importances_percentage})
    feature_importances_df = feature_importances_df.sort_values(by='Importance (%)', ascending=False)

    return feature_importances_df


def generate_plots(rf_importances_df: pd.DataFrame, pca_importances_df: pd.DataFrame,
                   ground_truth: pd.DataFrame) -> None:
    # Plot for Random Forest with a blue palette
    plt.figure(figsize=(12, 8))
    sns.barplot(x='Importance (%)', y='Feature', data=rf_importances_df, palette='Blues_r')
    plt.title('Feature Importances - Random Forest')
    plt.show()

    # Plot for PCA with a red palette
    plt.figure(figsize=(12, 8))
    sns.barplot(x='Importance (%)', y='Feature', data=pca_importances_df, palette='Reds_r')
    plt.title('Feature Importances - PCA')
    plt.show()

    # Plot for Ground Truth with a green palette
    plt.figure(figsize=(12, 8))
    sns.barplot(x='Importance (%)', y='Feature', data=ground_truth, palette='Greens_r')
    plt.title('Ground Truth Feature Importances')
    plt.show()


def calculate_spearman_coefficients(rf_importances_df: pd.DataFrame, pca_importances_df: pd.DataFrame,
                                    ground_truth: pd.DataFrame) -> None:
    # Align the data frames on the 'Feature' column
    merged_rf = pd.merge(rf_importances_df, ground_truth, on='Feature', suffixes=('_rf', '_gt'))
    merged_pca = pd.merge(pca_importances_df, ground_truth, on='Feature', suffixes=('_pca', '_gt'))

    # Calculate Spearman correlations
    rf_spearman_corr, _ = spearmanr(merged_rf['Importance (%)_rf'], merged_rf['Importance (%)_gt'])
    pca_spearman_corr, _ = spearmanr(merged_pca['Importance (%)_pca'], merged_pca['Importance (%)_gt'])

    print(f"Spearman Correlation (Random Forest vs Ground Truth): {rf_spearman_corr:.4f}")
    print(f"Spearman Correlation (PCA vs Ground Truth): {pca_spearman_corr:.4f}")


def generate_ground_truth_importances(data):
    # Calculate the correlation matrix
    correlation_matrix = data.corr()
    # Extract correlation with Disease_Outcome and drop the Disease_Outcome self-correlation
    ground_truth_importances = correlation_matrix['Disease_Outcome'].drop('Disease_Outcome').abs()
    ground_truth_importances.sort_values(ascending=False, inplace=True)
    # Normalize the importance to percentage
    ground_truth_importances *= 100 / ground_truth_importances.sum()
    ground_truth_importances_df = pd.DataFrame({
        'Feature': ground_truth_importances.index,
        'Importance (%)': ground_truth_importances.values
    })
    return ground_truth_importances_df


def main():
    output_dir = 'output'

    # Generate artificial dataset
    data = generate_data(num_samples=1000)

    # Generate ground truth importances based on correlation matrix
    ground_truth_importances = generate_ground_truth_importances(data)

    target_column = 'Disease_Outcome'

    # Perform Random Forest feature importance
    rf_importances_df = train_random_forest_model(data, target_column, max_depth=15, random_state=42)

    # Perform PCA feature importance
    pca_importances_df = perform_pca(data, target_column, n_components=2)

    # Generate plots
    generate_plots(rf_importances_df, pca_importances_df, ground_truth_importances)

    # Calculate and print Spearman coefficients
    calculate_spearman_coefficients(rf_importances_df, pca_importances_df, ground_truth_importances)


if __name__ == "__main__":
    main()
