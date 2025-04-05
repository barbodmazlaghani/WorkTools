import pandas as pd
import numpy as np

# Define the path to your Excel file
excel_file = r'C:\Users\bamir\Desktop\Repos\WorkTools\pm_synchronize\new_data\IPCO test 14031022.xlsx'

# Read the Concentration sheet
concentration_df = pd.read_excel(excel_file, sheet_name='Concentration')

# Read the Trip result sheet
trip_df = pd.read_excel(excel_file, sheet_name='Trip result')

# --- Handling the Concentration Data ---

# Check the data types of 'Date' and 'Time' columns
print("Concentration Data Types:")
print(concentration_df.dtypes[['Date', 'Time']])

# Since 'Time' already contains full datetime, use it directly
# Convert 'Time' to datetime if it's not already
if not pd.api.types.is_datetime64_any_dtype(concentration_df['Time']):
    concentration_df['Time'] = pd.to_datetime(concentration_df['Time'], errors='coerce')

# Check for any NaT values in 'Time'
if concentration_df['Time'].isnull().any():
    print("Warning: Some 'Time' entries could not be parsed and are set as NaT.")
    print(concentration_df[concentration_df['Time'].isnull()])

# Rename 'Time' to 'Datetime'
concentration_df = concentration_df.rename(columns={'Time': 'Datetime'})

# Drop the 'Date' column as it's redundant
concentration_df = concentration_df.drop(['Date'], axis=1)

# Set 'Datetime' as the index and sort
concentration_df = concentration_df.set_index('Datetime').sort_index()

# --- Handling Trip Result Data ---

# Convert 'timestamp' in Trip result to datetime
trip_df['Datetime'] = pd.to_datetime(trip_df['timestamp'], errors='coerce')

# Check for any NaT values in 'Datetime'
if trip_df['Datetime'].isnull().any():
    print("Warning: Some Trip Result 'timestamp' entries could not be parsed and are set as NaT.")
    print(trip_df[trip_df['Datetime'].isnull()])

# Drop unnecessary columns
trip_df = trip_df.drop(['time', 'timestamp_received', 'timestamp'], axis=1)

# Set 'Datetime' as the index and sort
trip_df = trip_df.set_index('Datetime').sort_index()

# --- Resampling ECU Data to 1/6 Hz (Every 6 Seconds) ---

# Resample the Trip data to 1/6 Hz by taking the mean every 6 seconds
trip_resampled = trip_df.resample('6s').mean()

# Reset index to have 'Datetime' as a column
trip_resampled = trip_resampled.reset_index()

# --- Merging Concentration and Trip Data ---

# Reset index on concentration_df to perform merge
concentration_reset = concentration_df.reset_index()

# Remove rows with NaT in 'Datetime' to prevent merge issues
concentration_reset = concentration_reset.dropna(subset=['Datetime'])
trip_resampled = trip_resampled.dropna(subset=['Datetime'])

# Merge using 'merge_asof' to align nearest datetimes within a 3-second tolerance
merged_df = pd.merge_asof(concentration_reset,
                          trip_resampled,
                          on='Datetime',
                          direction='nearest',
                          tolerance=pd.Timedelta('3s'))

# Check for any missing data after merge
missing_data = merged_df.isnull().sum()
if missing_data.any():
    print("Warning: Missing data detected in the merged dataset.")
    print(missing_data)

# --- Calculating Acceleration and Deceleration ---

# Sort by 'Datetime' to ensure correct order
merged_df = merged_df.sort_values('Datetime')

# Calculate speed difference
merged_df['Speed_Diff'] = merged_df['Vehicle_Speed'].diff()

# Calculate Acceleration and Deceleration
# Assuming the time interval is 6 seconds
merged_df['Acceleration'] = merged_df['Speed_Diff'].apply(lambda x: x / 6 if pd.notnull(x) and x > 0 else 0)
merged_df['Deceleration'] = merged_df['Speed_Diff'].apply(lambda x: -x / 6 if pd.notnull(x) and x < 0 else 0)

# Fill NaN values resulting from the diff operation
merged_df[['Acceleration', 'Deceleration']] = merged_df[['Acceleration', 'Deceleration']].fillna(0)

# Drop the 'Speed_Diff' column as it's no longer needed
merged_df = merged_df.drop(['Speed_Diff'], axis=1)

# --- Selecting and Reordering Columns ---

final_columns = [
    'Datetime',
    'TSP [ug/m3]',
    'PM10 [ug/m3]',
    'PM2.5 [ug/m3]',
    'PM1 [ug/m3]',
    'TC [1/l]',
    'Battery_voltage',
    'Electrical_load',
    'Switch',
    'Fuel_level',
    'Intake_manifold_absolute_pressure',
    'Throttle_position',
    'Accelerator_pedal_position',
    'Coolant_temperature',
    'Vehicle_Speed',
    'Engine_speed',
    'Target_air_fuel_ratio',
    'Estimated_catalyst_temperature',
    'Engine_status',
    'Status_bit',
    'Current_gear_shift_position_(Current_gear)',
    'Cumulative_mileage',
    'Clutch_torque',
    'Trip_fuel_consumption',
    'Average_fuel_consumption_rate',
    'Pumping_and_rubbing_friction_torque_at_current_condition',
    'RON_factor',
    'altitude',
    'latitude',
    'longitude',
    'satelites',
    'bearing',
    'angular_speed',
    'Acceleration',
    'Deceleration'
]

# Ensure all columns exist in the merged dataframe
final_columns = [col for col in final_columns if col in merged_df.columns]

final_df = merged_df[final_columns]

# --- Export to CSV ---

final_df.to_csv('synchronized_car_data_22.csv', index=False)

print("Synchronized CSV file 'synchronized_car_data.csv' has been created successfully.")
