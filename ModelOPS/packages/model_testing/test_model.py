import os
from pathlib import Path
from packages.processing import random_forest, lightGBM
from packages.model_testing.artificial_dataset_generation import generate_artificial_dataset
from packages.preprocessing import preprocess_data

root_path = Path(__file__).parent.parent.parent
testing_directory = os.path.join(root_path, "testing")
data_directory = os.path.join(testing_directory, "data")
clean_directory = os.path.join(testing_directory, "cleaned_data")
results_directory = os.path.join(testing_directory, "results")


def test_model():
    generate_artificial_dataset(data_directory)

    preprocess_data.preprocess_files(data_directory, output_directory=clean_directory, patient_identifier="", exclude_columns=["Disease_Outcome", 'Age'])
    lightGBM.run(clean_directory, results_directory, 'Disease_Outcome')


test_model()
