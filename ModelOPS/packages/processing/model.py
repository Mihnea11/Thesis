import os
import pandas as pd
import glob
from sklearn.model_selection import train_test_split
import joblib
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier


def train_random_forest(X_train, y_train, n_estimators=100, random_state=42):
    model = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test, y_test):
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    return accuracy


def save_model(model, path='random_forest_model.pkl'):
    joblib.dump(model, path)


def load_model(path='random_forest_model.pkl'):
    return joblib.load(path)


def merge_data(data_path):
    all_files = glob.glob(os.path.join(data_path, "*.csv"))
    df_from_each_file = (pd.read_csv(f) for f in all_files)
    concatenated_df = pd.concat(df_from_each_file, ignore_index=True)
    return concatenated_df


def run_model(data_path, key_column, save_model_path='random_forest_model.pkl'):
    # Merge data from files
    data = merge_data(data_path)

    # Split data into features and target
    X = data.drop(columns=[key_column])
    y = data[key_column]

    # Split dataset into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train the model
    model = train_random_forest(X_train, y_train)

    # Evaluate the model
    accuracy = evaluate_model(model, X_test, y_test)
    print(f"Model Accuracy: {accuracy}")

    # Save the model
    #save_model(model, save_model_path)

    # Optionally: Return model, accuracy, or any other information you need
    return model, accuracy


run_model(r"C:\Users\z004nwxe\Desktop\archive", "stage")