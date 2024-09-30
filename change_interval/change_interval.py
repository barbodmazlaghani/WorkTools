import pandas as pd
import numpy as np

# ==========================
# Configuration Parameters
# ==========================

# Path to your input Excel file
input_file = 'K125_NEDC_NIMA.xlsx'  # Update this path

# Path for the output resampled Excel file
output_file = 'resampled_data_NEDC.xlsx'  # Update this path

# Sheet name in the Excel file
sheet_name = 'K125_NIMA'  # Update if different

# Name of the time column
time_column = 'time'  # Ensure this matches your Excel file

# Time unit of the 'time' column
time_unit = 'ms'  # 'ms' for milliseconds

# Resampling frequency
resample_freq = '1S'  # '1S' stands for 1 second

# Aggregation method for additional columns
aggregation_method = 'mean'  # Options: 'mean', 'sum', 'first', 'last', etc.

# ==========================
# Step 1: Read the Excel File
# ==========================

try:
    df = pd.read_excel(input_file, sheet_name=sheet_name)
    print("Excel file loaded successfully.")
except Exception as e:
    print(f"Error reading Excel file: {e}")
    exit(1)

# ==========================
# Step 2: Validate the 'time' Column
# ==========================

if time_column not in df.columns:
    print(f"Error: The Excel file does not contain a '{time_column}' column.")
    exit(1)

# ==========================
# Step 3: Convert 'time' to Seconds
# ==========================

# Convert 'time' from milliseconds to seconds
df['time_sec'] = df[time_column] / 1000.0

# ==========================
# Step 4: Sort the DataFrame by 'time_sec'
# ==========================

df = df.sort_values('time_sec')

# ==========================
# Step 5: Define 1-Second Bins
# ==========================

# Create a new column for the 1-second bins
df['time_bin'] = df['time_sec'].astype(int)  # Floor to the nearest second

# ==========================
# Step 6: Group by 1-Second Bins and Aggregate
# ==========================

# Identify columns to aggregate (exclude 'time' and 'time_bin')
data_columns = [col for col in df.columns if col not in [time_column, 'time_sec', 'time_bin']]

# Group by 'time_bin' and aggregate
grouped = df.groupby('time_bin')[data_columns].agg(aggregation_method).reset_index()

# ==========================
# Step 7: Assign Exact 1-Second Timestamps
# ==========================

grouped['time'] = grouped['time_bin'] * 1000  # Convert back to milliseconds

# Optional: Round the 'time' column to integer if needed
grouped['time'] = grouped['time'].round().astype(int)

# ==========================
# Step 8: Arrange Columns
# ==========================

# Reorder columns to have 'time' first
cols = grouped.columns.tolist()
cols.insert(0, cols.pop(cols.index('time')))
grouped = grouped[cols]

# Drop the 'time_bin' column if not needed
grouped.drop(columns=['time_bin'], inplace=True)

# ==========================
# Step 9: Save to a New Excel File
# ==========================

try:
    grouped.to_excel(output_file, index=False)
    print(f"Resampled data saved successfully to {output_file}")
except Exception as e:
    print(f"Error saving resampled data: {e}")
    exit(1)
