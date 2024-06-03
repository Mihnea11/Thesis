import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def generate_data(num_samples: int = 1000) -> pd.DataFrame:
    np.random.seed(42)

    age = np.random.normal(50, 12, num_samples).round(0).astype(int)
    cholesterol = np.random.normal(100, 200, num_samples).round(1) + age
    systolic_bp = np.random.normal(120, 15, num_samples).round(1)
    diastolic_bp = np.random.normal(80, 10, num_samples).round(1)
    bmi = np.random.normal(25, 4, num_samples).round(1)
    glucose = np.random.normal(100, 20, num_samples).round(1)
    inflammation_marker = np.abs(np.random.normal(0, 1, num_samples).round(2))
    oxidative_stress_marker = np.abs((2 * inflammation_marker + np.random.normal(0, 0.5, num_samples)).round(2))

    disease_score = (0.03 * age + 0.03 * cholesterol + 0.04 * systolic_bp + 0.06 * bmi + 0.03 * glucose + 0.03 * inflammation_marker + 0.1 * oxidative_stress_marker + np.random.normal(1.5, 3, num_samples)).round(2)
    disease = pd.cut(disease_score, bins=[-np.inf, 5, 10, 15, np.inf], labels=[0, 1, 2, 3])

    data = pd.DataFrame({
        'Age': age,
        'Cholesterol': cholesterol,
        'Systolic_BP': systolic_bp,
        'Diastolic_BP': diastolic_bp,
        'BMI': bmi,
        'Glucose': glucose,
        'Inflammation_Marker': inflammation_marker,
        'Oxidative_Stress_Marker': oxidative_stress_marker,
        'Disease_Outcome': disease
    })

    return data


def generate_correlation_matrix(data: pd.DataFrame):
    correlation_matrix = data.corr()
    return correlation_matrix


def save_correlation_matrix_as_png(correlation_matrix: pd.DataFrame, output_path: str):
    plt.figure(figsize=(20, 15))
    sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap='coolwarm', cbar=True)
    plt.title('Correlation Matrix')
    plt.savefig(output_path)
    plt.close()


def visualize_biomarkers_vs_disease(data: pd.DataFrame, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    for column in data.columns[:-1]:  # Exclude the disease outcome column
        plt.figure(figsize=(10, 6))
        sns.boxplot(x='Disease_Outcome', y=column, data=data)
        plt.title(f'{column} vs Disease Outcome')
        plt.savefig(os.path.join(output_dir, f'{column}_vs_disease.png'))
        plt.close()


def generate_artificial_dataset(output_dir: str, num_samples: int = 1000) -> None:
    generated_data = generate_data(num_samples)
    correlation_matrix = generate_correlation_matrix(generated_data)

    os.makedirs(output_dir, exist_ok=True)
    generated_data.to_csv(os.path.join(output_dir, 'artificial_dataset.csv'), index=False)
    save_correlation_matrix_as_png(correlation_matrix, os.path.join(output_dir, 'correlation_matrix.png'))
    visualize_biomarkers_vs_disease(generated_data, output_dir)

    print("Dataset, correlation matrix, and visualizations saved successfully.")


# Specify the output directory and generate the dataset
output_dir = r'D:\Projects\Thesis\ModelOPS\testing\data'
generate_artificial_dataset(output_dir, num_samples=1000)
