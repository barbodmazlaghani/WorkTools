import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os


def feature_engineering_new(df, time_col, speed_col):
    """
    Perform feature engineering on the new dataset by detecting trips based on 'time' resets.
    """
    # Detect trip boundaries where 'time' resets or decreases
    df = df.sort_values(by=time_col).reset_index(drop=True)
    df['trip_id'] = (df[time_col].diff() < 0).cumsum()

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

    df = df.groupby('trip_id').apply(process_trip).reset_index(drop=True)
    return df


def predict_gear():
    print("=== Gear Prediction on New Data ===\n")

    # User Inputs for Prediction
    NEW_FILE_PATH = input("Enter the new data Excel file path (e.g., C:\\path\\to\\new_file.xlsx): ").strip('"').strip(
        "'")
    NEW_SHEET_NAME = input("Enter the new data sheet name (e.g., wltc class 3): ")
    NEW_TIME_COL = input("Enter the 'time' column name in new data (e.g., time): ")
    NEW_SPEED_COL = input("Enter the 'Vehicle_Speed' column name in new data (e.g., Vehicle_Speed): ")
    MODEL_PATH = input("Enter the path to the trained model file (e.g., gear_model.pkl): ").strip('"').strip("'")
    PREDICTION_OUTPUT_PATH = input("Enter the path to save the predicted data (e.g., new_data_with_gear.xlsx): ").strip(
        '"').strip("'")

    # Check if model exists
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"The model file '{MODEL_PATH}' does not exist. Please train the model first.")

    # Load the trained model
    print("\nLoading the trained model...")
    model = joblib.load(MODEL_PATH)
    print(f"Model loaded from '{MODEL_PATH}'.")

    # Load new data
    print("Loading new data...")
    df_new = pd.read_excel(NEW_FILE_PATH, sheet_name=NEW_SHEET_NAME)
    print(f"Original New Data Shape: {df_new.shape}")

    # Check required columns
    required_cols = [NEW_TIME_COL, NEW_SPEED_COL]
    missing_cols = [col for col in required_cols if col not in df_new.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in new data: {missing_cols}")

    # Feature Engineering
    print("Performing feature engineering on new data...")
    df_new = feature_engineering_new(df_new, NEW_TIME_COL, NEW_SPEED_COL)

    # Define feature columns
    feature_cols = [
        'speed',
        'acceleration',
        'speed_lag_1', 'speed_lag_2', 'speed_lag_3',
        'acceleration_lag_1', 'acceleration_lag_2', 'acceleration_lag_3',
        'speed_rolling_mean',
        'speed_rolling_std'
    ]

    # Drop rows with NaN in feature columns
    print("Cleaning new data by removing rows with NaN values in features...")
    df_clean_new = df_new.dropna(subset=feature_cols).reset_index(drop=True)
    print(f"Cleaned New Data Shape: {df_clean_new.shape}")

    # Prepare feature matrix
    X_new = df_clean_new[feature_cols].values

    # Predict gear
    print("Predicting gear for new data...")
    predicted_gear = model.predict(X_new)
    df_clean_new['predicted_gear'] = predicted_gear

    # Optionally map back to original gear codes if needed
    # For example, if 0 was Neutral and 1 was Reverse during training
    # You can extend this mapping based on your specific gear encoding
    # df_clean_new['predicted_gear_original'] = df_clean_new['predicted_gear'].replace({0:13, 1:14})

    # Merge predictions back to the original dataframe
    # Since we dropped some rows, it's better to merge based on index or another identifier
    # Here, we'll append the predictions to the cleaned dataframe
    # If you wish to keep all original data points, consider alternative merging strategies

    # Save the predictions to a new Excel file
    print(f"Saving the predicted data to '{PREDICTION_OUTPUT_PATH}'...")
    df_clean_new.to_excel(PREDICTION_OUTPUT_PATH, index=False)
    print("Predicted gear saved successfully!")


if __name__ == "__main__":
    predict_gear()
