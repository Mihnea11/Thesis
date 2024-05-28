import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def generate_data(num_samples: int = 1000) -> pd.DataFrame:
    np.random.seed(42)
    biomarker_1 = np.random.normal(0, 1, num_samples).round(5)
    biomarker_2 = (3 * biomarker_1 + np.random.normal(0, 0.5, num_samples)).round(5)
    biomarker_3 = (biomarker_1**2 + np.random.normal(0, 0.2, num_samples)).round(5)
    biomarker_4 = np.random.normal(0, 1, num_samples).round(5)
    biomarker_5 = (0.5 * biomarker_3 + np.random.normal(0, 0.1, num_samples)).round(5)
    disease_score = (2 * biomarker_1 - 0.5 * biomarker_2 + 1.5 * biomarker_3 + np.random.normal(0, 1, num_samples)).round(5)
    disease = pd.cut(disease_score, bins=[-np.inf, -1, 1, np.inf], labels=[0, 1, 2])

    data = pd.DataFrame({
        'Biomarker_1': biomarker_1,
        'Biomarker_2': biomarker_2,
        'Biomarker_3': biomarker_3,
        'Biomarker_4': biomarker_4,
        'Biomarker_5': biomarker_5,
        'Disease_Outcome': disease
    })

    return data


def generate_correlation_matrix(data: pd.DataFrame):
    correlation_matrix = data.corr()
    return correlation_matrix


def save_correlation_matrix_as_png(correlation_matrix: pd.DataFrame, output_path: str):
    plt.figure(figsize=(15, 10))
    sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap='coolwarm', cbar=True)
    plt.title('Correlation Matrix')
    plt.savefig(output_path)
    plt.close()


def generate_artificial_dataset(output_dir: str, num_samples: int = 1000) -> None:
    generated_data = generate_data(num_samples)
    correlation_matrix = generate_correlation_matrix(generated_data)

    os.makedirs(output_dir, exist_ok=True)
    generated_data.to_csv(os.path.join(output_dir, 'artificial_dataset.csv'), index=False)
    save_correlation_matrix_as_png(correlation_matrix, os.path.join(output_dir, 'correlation_matrix.png'))

    print("Dataset, correlation matrix CSV and PNG saved successfully.")

