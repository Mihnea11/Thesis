import re
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Optional


age_aliases = ['age', 'age_patient', 'age_number']
gender_aliases = ['gender', 'sex']


def find_column_name(columns: List[str], aliases: List[str]) -> Optional[str]:
    """
    Find the column name matching any of the aliases, case-insensitively.

    :param columns: List of column names in the dataset.
    :param aliases: List of aliases to match against column names.
    :return: The matched column name or None if no match is found.
    """
    for alias in aliases:
        pattern = re.compile(fr'^{alias}$', re.IGNORECASE)
        for col in columns:
            if re.match(pattern, col):
                return col
    return None


def aggregate_patient_data(files: List[str], id_col_name: str) -> pd.DataFrame:
    """
    Aggregate data from multiple files to get unique patient data.

    :param files: List of file paths to CSV files containing patient data.
    :param id_col_name: The column name representing patient IDs.
    :return: A DataFrame with unique patient data aggregated from all files.
    """
    all_data = []
    for file_path in files:
        data = pd.read_csv(file_path)
        all_data.append(data)

    combined_data = pd.concat(all_data, ignore_index=True)
    unique_patients = combined_data.drop_duplicates(subset=[id_col_name])

    return unique_patients


def process_files(files: List[str], target_column: str, id_col_name: str, output_dir: str) -> None:
    """
    Process the files to generate various insights and plots.

    :param files: List of file paths to CSV files containing patient data.
    :param target_column: The name of the target variable column in the dataset.
    :param id_col_name: The column name representing patient IDs.
    :param output_dir: Directory where the output plots will be saved.
    :return: None
    """
    combined_data = aggregate_patient_data(files, id_col_name)

    age_col = find_column_name(combined_data.columns, age_aliases)
    gender_col = find_column_name(combined_data.columns, gender_aliases)

    if not target_column or not age_col:
        print(f"Required columns not found in the provided files.")
        return

    if combined_data[target_column].dtype == object:
        combined_data[target_column] = combined_data[target_column].str.lower().map({'yes': 1, 'no': 0})

    combined_data['Health Status'] = combined_data[target_column].apply(lambda x: 'Healthy' if x == 0 else 'Unhealthy')
    health_counts = combined_data['Health Status'].value_counts()

    plt.figure(figsize=(12, 8))
    health_counts.plot.pie(autopct='%1.1f%%', startangle=90, colors=sns.color_palette("viridis"))
    plt.title('Healthy vs Unhealthy Patients')
    plt.ylabel('')

    total_patients = len(combined_data)
    healthy_patients = health_counts['Healthy']
    unhealthy_patients = health_counts['Unhealthy']

    textstr = f'Total Patients: {total_patients}\nHealthy: {healthy_patients}\nUnhealthy: {unhealthy_patients}'
    plt.gcf().text(0.15, 0.85, textstr, fontsize=12, bbox=dict(facecolor='white', alpha=0.5))

    plt.savefig(os.path.join(output_dir, 'health_counts_pie.png'))
    plt.close()

    if gender_col:
        distribution_by_gender = combined_data.groupby(['Health Status', gender_col]).size().unstack(fill_value=0)
        distribution_by_gender.plot(kind='bar', stacked=True, figsize=(12, 8), colormap='viridis')
        plt.title('Disease Distribution by Health Status and Gender')
        plt.xlabel('Health Status')
        plt.ylabel('Number of Patients')
        plt.savefig(os.path.join(output_dir, 'distribution_by_gender.png'))
        plt.close()

    if age_col:
        plt.figure(figsize=(12, 8))
        sns.histplot(data=combined_data[combined_data[target_column] != 0], x=age_col, bins=20, kde=True,
                     color=sns.color_palette("viridis")[0])
        plt.title('Disease Distribution Across Age')
        plt.xlabel('Age')
        plt.ylabel('Number of Patients')
        plt.savefig(os.path.join(output_dir, 'age_distribution.png'))
        plt.close()


def analyze(input_dir: str, output_dir: str, target_column: str, id_col_name: str) -> None:
    """
    Main function to execute the analysis.

    :param input_dir: Directory containing the input CSV files.
    :param output_dir: Directory where the output plots and analysis will be saved.
    :param target_column: The name of the target variable column in the dataset.
    :param id_col_name: The column name representing patient IDs.
    :return: None
    """
    print("Starting dataset analysis")
    save_dir = os.path.join(output_dir, "stats")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.csv')]

    process_files(files, target_column, id_col_name, save_dir)
    print("Analysis complete. Results and plots are saved.")
