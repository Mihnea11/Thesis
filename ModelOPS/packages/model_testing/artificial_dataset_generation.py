import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def generate_data(num_samples: int = 1000) -> pd.DataFrame:
    np.random.seed(42)

    # Define proportions for each disease stage
    proportions = [0.25, 0.25, 0.25, 0.25]
    stage_samples = [int(num_samples * p) for p in proportions]

    def generate_stage_data(num_samples, stage):
        if stage == 0:
            # Healthy
            age = np.random.normal(40, 10, num_samples).round(0).astype(int)
            bmi = np.random.normal(22, 3, num_samples).round(1)
            glucose = np.random.normal(90, 10, num_samples).round(1)
            systolic_bp = np.random.normal(115, 10, num_samples).round(1)
            diastolic_bp = np.random.normal(75, 8, num_samples).round(1)
            cholesterol = np.random.normal(180, 20, num_samples).round(1)
            inflammation_marker = np.abs(np.random.normal(0.2, 0.1, num_samples).round(2))
            oxidative_stress_marker = np.abs(np.random.normal(0.2, 0.1, num_samples).round(2))
        elif stage == 1:
            # Early stage
            age = np.random.normal(50, 12, num_samples).round(0).astype(int)
            bmi = np.random.normal(25, 4, num_samples).round(1)
            glucose = np.random.normal(100, 15, num_samples).round(1)
            systolic_bp = np.random.normal(120, 12, num_samples).round(1)
            diastolic_bp = np.random.normal(80, 10, num_samples).round(1)
            cholesterol = np.random.normal(200, 25, num_samples).round(1)
            inflammation_marker = np.abs(np.random.normal(0.5, 0.2, num_samples).round(2))
            oxidative_stress_marker = np.abs(np.random.normal(0.5, 0.2, num_samples).round(2))
        elif stage == 2:
            # Mid stage
            age = np.random.normal(55, 12, num_samples).round(0).astype(int)
            bmi = np.random.normal(28, 5, num_samples).round(1)
            glucose = np.random.normal(120, 20, num_samples).round(1)
            systolic_bp = np.random.normal(130, 15, num_samples).round(1)
            diastolic_bp = np.random.normal(85, 10, num_samples).round(1)
            cholesterol = np.random.normal(220, 30, num_samples).round(1)
            inflammation_marker = np.abs(np.random.normal(0.8, 0.3, num_samples).round(2))
            oxidative_stress_marker = np.abs(np.random.normal(0.8, 0.3, num_samples).round(2))
        else:
            # Advanced stage
            age = np.random.normal(60, 12, num_samples).round(0).astype(int)
            bmi = np.random.normal(32, 6, num_samples).round(1)
            glucose = np.random.normal(140, 25, num_samples).round(1)
            systolic_bp = np.random.normal(140, 20, num_samples).round(1)
            diastolic_bp = np.random.normal(90, 12, num_samples).round(1)
            cholesterol = np.random.normal(240, 35, num_samples).round(1)
            inflammation_marker = np.abs(np.random.normal(1.0, 0.4, num_samples).round(2))
            oxidative_stress_marker = np.abs(np.random.normal(1.0, 0.4, num_samples).round(2))

        data = pd.DataFrame({
            'Age': age,
            'BMI': bmi,
            'Glucose': glucose,
            'Systolic_BP': systolic_bp,
            'Diastolic_BP': diastolic_bp,
            'Cholesterol': cholesterol,
            'Inflammation_Marker': inflammation_marker,
            'Oxidative_Stress_Marker': oxidative_stress_marker,
            'Disease_Outcome': [stage] * num_samples
        })

        return data

    # Generate data for each stage
    data = pd.concat([
        generate_stage_data(stage_samples[0], 0),
        generate_stage_data(stage_samples[1], 1),
        generate_stage_data(stage_samples[2], 2),
        generate_stage_data(stage_samples[3], 3)
    ], ignore_index=True)

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
    generated_data.to_csv(os.path.join(output_dir, 't2d_dataset.csv'), index=False)
    save_correlation_matrix_as_png(correlation_matrix, os.path.join(output_dir, 'correlation_matrix.png'))
    visualize_biomarkers_vs_disease(generated_data, output_dir)

    print("Dataset, correlation matrix, and visualizations saved successfully.")

# Specify the output directory and generate the dataset
output_dir = r'D:\Projects\Thesis\ModelOPS\testing\data'
generate_artificial_dataset(output_dir, num_samples=1000)
