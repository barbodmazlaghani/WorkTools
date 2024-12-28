import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os


def feature_engineering(df, time_col, speed_col, trip_col):
    """
    Perform feature engineering on the dataset grouped by trips.
    """

    def process_trip(group):
        group = group.sort_values(time_col).reset_index(drop=True)
        group['speed'] = group[speed_col]
        group['acceleration'] = group['speed'].diff().fillna(0)

        # Create lag features
        for i in range(1, 4):
            group[f'speed_lag_{i}'] = group['speed'].shift(i)
            group[f'acceleration_lag_{i}'] = group['acceleration'].shift(i)

        # Create rolling features
        group['speed_rolling_mean'] = group['speed'].rolling(window=5, min_periods=1).mean()
        group['speed_rolling_std'] = group['speed'].rolling(window=5, min_periods=1).std().fillna(0)

        return group

    df = df.groupby(trip_col).apply(process_trip).reset_index(drop=True)
    return df


def train_model():
    print("=== Model Training ===\n")

    # User Inputs for Training Data
    TRAIN_FILE_PATH = input("Enter the training data Excel file path (e.g., C:\\path\\to\\file.xlsx): ").strip(
        '"').strip("'")
    TRAIN_SHEET_NAME = input("Enter the training data sheet name (e.g., Data): ")
    TRAIN_TIME_COL = input("Enter the 'time' column name in training data (e.g., time): ")
    TRAIN_SPEED_COL = input("Enter the 'Vehicle_Speed' column name in training data (e.g., Vehicle_Speed): ")
    TRAIN_TRIP_COL = input("Enter the 'trip' column name in training data (e.g., trip): ")
    TRAIN_GEAR_COL = input(
        "Enter the 'Current_gear_shift_position_(Current_gear)' column name in training data (e.g., Current_gear_shift_position_(Current_gear)): ")
    MODEL_OUTPUT_PATH = input("Enter the path to save the trained model (e.g., gear_model.pkl): ").strip('"').strip("'")

    # Load training data
    print("\nLoading training data...")
    df = pd.read_excel(TRAIN_FILE_PATH, sheet_name=TRAIN_SHEET_NAME)
    print(f"Original Data Shape: {df.shape}")

    # Check required columns
    required_cols = [TRAIN_TIME_COL, TRAIN_SPEED_COL, TRAIN_TRIP_COL, TRAIN_GEAR_COL]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in training data: {missing_cols}")

    # Remap gear values: 13 -> 0 (Neutral), 14 -> 1 (Reverse), keep others as is
    print("Remapping gear values...")
    df['gear'] = df[TRAIN_GEAR_COL].replace({13: 0, 14: 1})

    # Feature Engineering
    print("Performing feature engineering...")
    df = feature_engineering(df, TRAIN_TIME_COL, TRAIN_SPEED_COL, TRAIN_TRIP_COL)

    # Define feature columns
    feature_cols = [
        'speed',
        'acceleration',
        'speed_lag_1', 'speed_lag_2', 'speed_lag_3',
        'acceleration_lag_1', 'acceleration_lag_2', 'acceleration_lag_3',
        'speed_rolling_mean',
        'speed_rolling_std'
    ]

    # Drop rows with NaN in feature columns or gear
    print("Cleaning data by removing rows with NaN values in features or target...")
    df_clean = df.dropna(subset=feature_cols + ['gear']).reset_index(drop=True)
    print(f"Cleaned Data Shape: {df_clean.shape}")

    # Prepare feature matrix and target vector
    X = df_clean[feature_cols].values
    y = df_clean['gear'].values

    # Split data into Train, Validation, and Test sets (70%, 15%, 15%)
    print("Splitting data into Train, Validation, and Test sets...")
    X_trainval, X_test, y_trainval, y_test = train_test_split(
        X, y, test_size=0.15, shuffle=False
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_trainval, y_trainval, test_size=0.1765, shuffle=False
    )
    # 0.1765 * 0.85 ≈ 0.15 of total data for validation

    print(f"Training Set Size: {X_train.shape[0]}")
    print(f"Validation Set Size: {X_val.shape[0]}")
    print(f"Test Set Size: {X_test.shape[0]}")

    # Hyperparameter Tuning with GridSearchCV
    print("\nStarting hyperparameter tuning with GridSearchCV...")
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [5, 10, 20],
        'min_samples_leaf': [1, 5, 10]
    }

    clf = GridSearchCV(
        RandomForestClassifier(random_state=42),
        param_grid,
        cv=3,
        scoring='accuracy',
        n_jobs=-1
    )

    clf.fit(X_train, y_train)
    print("GridSearchCV completed.")
    print(f"Best Parameters: {clf.best_params_}")

    # Evaluate on Validation Set
    print("\nEvaluating on Validation Set...")
    y_val_pred = clf.predict(X_val)
    print("Validation Classification Report:")
    print(classification_report(y_val, y_val_pred))

    # Final Evaluation on Test Set
    print("Evaluating on Test Set...")
    final_model = clf.best_estimator_
    y_test_pred = final_model.predict(X_test)
    print("Test Classification Report:")
    print(classification_report(y_test, y_test_pred))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_test_pred))

    # Save the trained model
    print(f"\nSaving the trained model to '{MODEL_OUTPUT_PATH}'...")
    joblib.dump(final_model, MODEL_OUTPUT_PATH)
    print("Model saved successfully!")


if __name__ == "__main__":
    train_model()
