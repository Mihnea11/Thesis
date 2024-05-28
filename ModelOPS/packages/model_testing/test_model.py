import os
from pathlib import Path
from packages.processing import random_forest
from packages.model_testing.artificial_dataset_generation import generate_artificial_dataset


root_path = Path(__file__).parent.parent.parent
testing_directory = os.path.join(root_path, "testing")
data_directory = os.path.join(testing_directory, "data")
results_directory = os.path.join(testing_directory, "results")


def test_model():
    generate_artificial_dataset(data_directory)

    random_forest.run(data_directory, results_directory, 'Disease_Outcome')


test_model()


