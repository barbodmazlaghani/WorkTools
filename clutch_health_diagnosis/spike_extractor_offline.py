import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

# Paths to driver reference data and the folder containing the driver CSV files
driver_data_path = 'E:\\علم داده\\Project_01\\drivers_refined\\driver-data.xlsx'
folder_path = 'E:\\علم داده\\Project_01\\drivers_refined\\80 Drivers'

# Load driver reference data
driver_data = pd.read_excel(driver_data_path)

# Initialize the results DataFrame
spike_results = pd.DataFrame(columns=[
    'driver', 'driver_n', 'from_gear', 'to_gear', 'row_number',
    'spike_length_percentage', 'spike_pattern'
])

# Threshold for detecting a spike pattern
threshold = 5  # Spike length percentage threshold (e.g., 5%)

# Window size around the gear shift to analyze
window_size = 5  # Number of rows before and after the gear shift

# Process each CSV file in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)
        df = pd.read_csv(file_path)

        # Reset index to have consistent row numbers
        df.reset_index(drop=True, inplace=True)

        # Match driver data from the reference file
        filename_key = filename.replace("_refined", "")
        driver_row = driver_data[driver_data['fileName'] == filename_key]

        # Convert gear positions to numerical values
        gear_map = {"N": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6}
        df["Current gear shift position"].replace(gear_map, inplace=True)

        # Convert to numeric and handle errors
        df['Current gear shift position'] = pd.to_numeric(df['Current gear shift position'], errors='coerce')

        # Check for any remaining non-numeric values
        if df['Current gear shift position'].isnull().any():
            print(f"Non-numeric gear positions found in {filename}.")
            # Drop rows with NaN gear positions
            df.dropna(subset=['Current gear shift position'], inplace=True)

        # Filter out rows with abnormal or zero engine speed values to avoid division errors
        df = df[(df['Engine speed'] > 0) & (df['Speed'] > 0)]

        # Reset index after filtering
        df.reset_index(drop=True, inplace=True)

        # Calculate gear ratio
        df['gear_ratio'] = df['Speed'] / df['Engine speed']

        # Calculate baseline gear ratio for each gear position
        baseline_ratios = df.groupby('Current gear shift position')['gear_ratio'].median()
        df['baseline_ratio'] = df['Current gear shift position'].map(baseline_ratios)

        # Identify gear shifts
        df['gear_shift'] = df['Current gear shift position'].diff().ne(0)

        # Get indices where gear shifts occur
        gear_shift_indices = df.index[df['gear_shift']].tolist()

        # For each gear shift, analyze the spike pattern
        for idx in gear_shift_indices:
            if idx == 0 or idx >= len(df) - 1:
                continue  # Skip if index is out of bounds

            from_gear = df.loc[idx - 1, 'Current gear shift position']
            to_gear = df.loc[idx, 'Current gear shift position']

            # Define the window around the gear shift
            start_idx = max(idx - window_size, 0)
            end_idx = min(idx + window_size, len(df) - 1)
            window_df = df.loc[start_idx:end_idx].copy()

            # Calculate deviations from baseline for the window
            window_df['deviation_from_baseline'] = np.abs(window_df['gear_ratio'] - window_df['baseline_ratio'])

            # Find the maximum deviation in the window
            max_deviation = window_df['deviation_from_baseline'].max()
            max_deviation_idx = window_df['deviation_from_baseline'].idxmax()

            # Get the baseline ratios before and after the gear shift
            baseline_ratio_old = baseline_ratios.get(from_gear, np.nan)
            baseline_ratio_new = baseline_ratios.get(to_gear, np.nan)

            # Skip if any baseline ratio is NaN or zero
            if np.isnan(baseline_ratio_old) or np.isnan(baseline_ratio_new):
                continue
            if baseline_ratio_old == 0 or baseline_ratio_new == 0:
                continue

            # Calculate spike length as percentage of baseline ratio
            spike_length_percentage = (max_deviation / baseline_ratio_old) * 100  # Relative to old gear

            # Determine spike pattern (increase or decrease)
            gear_ratio_before = df.loc[idx - 1, 'gear_ratio']
            gear_ratio_after = df.loc[idx, 'gear_ratio']

            if gear_ratio_after > gear_ratio_before:
                spike_pattern = 'Upward Spike'
            else:
                spike_pattern = 'Downward Spike'

            # Check if the spike meets the threshold criteria
            if spike_length_percentage >= threshold:
                # Append the spike data
                spike_results = spike_results.append({
                    'driver': driver_row['driver_name_english'].values[0] if not driver_row.empty else 'Unknown',
                    'driver_n': driver_row['fileName'].values[0] if not driver_row.empty else 'Unknown',
                    'from_gear': from_gear,
                    'to_gear': to_gear,
                    'row_number': max_deviation_idx,
                    'spike_length_percentage': spike_length_percentage,
                    'spike_pattern': spike_pattern
                }, ignore_index=True)

# Save the spike results to an Excel file
spike_results.to_excel('clutch_spike_pattern_analysis.xlsx', index=False)

# Calculate the average spike length percentage for each driver
average_spike_length = spike_results.groupby(['driver', 'driver_n'])['spike_length_percentage'].mean().reset_index()

# Save the average spike length per driver to a new Excel file
average_spike_length.to_excel('average_spike_length_per_driver.xlsx', index=False)

# Optional: Plot the distribution of average spike lengths
plt.figure(figsize=(10, 6))
plt.hist(average_spike_length['spike_length_percentage'], bins=30, edgecolor='black')
plt.xlabel('Average Spike Length (%)')
plt.ylabel('Number of Drivers')
plt.title('Distribution of Average Spike Lengths per Driver')
plt.show()
