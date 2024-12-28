import pandas as pd
import os
import numpy as np

DISTANCE_DIVIDE_AMOUNT = 2
# MIN_ISLAND_DISTANCE = 1  # Removed as per your request

DIVIDE_BY_KM = False

def divide_driver_step_by_km(df, km, group_offset):
    res = []
    df['distance_group'] = group_offset + (df['Cumulative_mileage'] - df['Cumulative_mileage'].iloc[0]) // km
    for name, df2 in df.groupby('distance_group'):
        res.append(df2)
    return res

# command = input("create file for each step? (press y for yes or n for no) : ")
create_file = False
# if command.strip().lower() == 'y' :
#     create_file = True

while True:

    columns = [
        'file_name', 'Island_number', 'Island_time', 'Island_distance', 'Island_fuel_consumption',
        'fuel_consumption_mean', "speed_std", "speed_max", "speed_mean", "clutch_torque_mean",
        "acceleration_mean",
        "acceleration_std", "deceleration_mean", "deceleration_std", "engine_speed_mean",
        "accelerator_pedal_position_mean", "accelerator_pedal_position_std", "engine_speed_std",
        "battery_voltage_mean",
        "current_gear_shift_position_mean", "throttle_position_mean", "island_start_row", "island_end_row",
        "IDLE_percentage", "average_spike_length_percentage", "average_load_hp"  # Added "average_load_hp"
    ]  # Updated names and added island row info

    dff = pd.DataFrame(columns=columns)
    address = input("Enter folder address (or press Enter to exit): ")
    if address == '':
        break
    log_count = 0
    for root, dirs, files in os.walk(address):
        for file in files:
            if file.startswith('~') or file.split('.')[-1] not in ['xlsx', 'csv'] or file == 'DTC.xlsx':
                continue
            try:
                file_path = os.path.join(root, file)
                print(f"Processing file: {file_path}")
                df = None
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)

                group_offset = 0
                df.drop(0, inplace=True)
                df.reset_index(drop=True, inplace=True)  # Reset index after dropping rows

                # Handle 'Consumed fuel' column if present
                if 'Consumed fuel' in df.columns:
                    df['Consumed fuel'] = df['Consumed fuel'].astype(float) * 1000000

                # Rename columns for consistency
                df.rename(columns={
                    'Clutch_torque_(Engine_Torque)': 'Clutch_torque',
                    'Cumulative mileage': 'Cumulative_mileage',
                    'Current_gear_shift_position_(Gear_State)': 'Current_gear_shift_position',
                    'Consumed fuel': 'Trip_fuel_consumption',
                    'Total mileage of vehicle': 'Cumulative_mileage',
                    'Vehicle speed': 'Vehicle_Speed',
                    'Engine speed': 'Engine_speed',
                    'throttle angle with respect to lower mechanical stop': 'Throttle_position',
                    'Normalized angle acceleration pedal': 'Accelerator_pedal_position',
                    'Battery voltage (on board), conversed to standard quantization and low pass filter': 'Battery_voltage',
                    'Engaged gear': 'Current_gear_shift_position'
                }, inplace=True)

                input_columns = [
                    'Time', 'Trip_fuel_consumption', 'Vehicle_Speed', 'Engine_speed',
                    'Accelerator_pedal_position', 'Clutch_torque', 'Cumulative_mileage',
                    'Battery_voltage', 'Current_gear_shift_position', 'Throttle_position'
                ]
                for col in input_columns:
                    if col not in df.columns:
                        df[col] = np.nan
                if not create_file:
                    df = df[input_columns]
                    df = df.astype(float)
                else:
                    for col in input_columns:
                        df[col] = df[col].astype(float)

                # ======== Start of High Load Filtering ======== #
                # Calculate load as Engine_speed * Clutch_torque
                df['load'] = df['Engine_speed'] * df['Clutch_torque']

                # Calculate load in horsepower
                df['load_hp'] = (df['Clutch_torque'] * df['Engine_speed'] * 2 * np.pi / 60) / 745.7

                # Determine the maximum load in the current file (using load in Nm)
                max_load = df['load'].max()
                print(max_load)
                # Set the threshold to 80% of the maximum load
                load_threshold = 0.8 * max_load

                # Identify high load condition
                df['high_load'] = df['load'] > load_threshold

                # Identify islands by finding continuous high_load segments
                df['island_group'] = (df['high_load'] != df['high_load'].shift()).cumsum()
                islands = df[df['high_load']].groupby('island_group')

                # ======== End of High Load Filtering ======== #

                trips_folder = file_path.split('\\')[-1] + "_steps"
                if create_file:
                    try:
                        os.mkdir(trips_folder)
                    except:
                        pass
                file_name = "\\".join(file_path.split('\\')[-2:])

                # Processing each island
                laststepTime = 0
                island_num = 1
                for group_id, island in islands:
                    if DIVIDE_BY_KM:
                        step_list = divide_driver_step_by_km(island, DISTANCE_DIVIDE_AMOUNT, group_offset)
                    else:
                        step_list = [island]
                    for step in step_list:
                        if len(step) < 2:
                            continue
                        km = step['Cumulative_mileage'].iloc[-1] - step['Cumulative_mileage'].iloc[0]
                        # Removed the distance-based filtering
                        step.loc[step.index[0], 'time_diff'] = 0

                        # Calculate island time
                        step_time = step.loc[step['time_diff'] < 10000, 'time_diff'].sum() / 3600000

                        # Calculate fuel consumption
                        step['momentary_fuel_consumption'] = step['Trip_fuel_consumption'].diff()
                        step_fuel = step.loc[((step['momentary_fuel_consumption'] > 0) & (
                                    step['momentary_fuel_consumption'] < 199999)), 'momentary_fuel_consumption'].sum() / 1000000

                        # Calculate speed statistics
                        speed_avg = step['Vehicle_Speed'].mean()
                        speed_std = step['Vehicle_Speed'].std()
                        speed_max = step['Vehicle_Speed'].max()
                        Clutch_torque = step['Clutch_torque'].mean()

                        # Calculate acceleration and deceleration
                        step['time_diff'] = step['Time'].diff() / 1000  # time_diff in seconds

                        # Replace zero time_diff with NaN to avoid division by zero
                        step['time_diff'].replace(0, np.nan, inplace=True)

                        # Calculate acceleration
                        step['acceleration'] = step['Vehicle_Speed'].diff() / (3.6 * step['time_diff'])
                        step['acceleration'].fillna(0, inplace=True)  # Replace NaN with 0 or handle as desired

                        # Calculate deceleration
                        step['deceleration'] = step.loc[step['acceleration'] < 0, 'acceleration'].abs()
                        step.loc[step['acceleration'] < 0, 'acceleration'] = np.nan

                        # Calculate IDLE_percentage
                        idle_count = len(step[(step['Engine_speed'] != 0) & (step['Vehicle_Speed'] == 0)])
                        total_count = len(step)
                        IDLE_percentage = (idle_count / total_count) * 100 if total_count > 0 else 0

                        off_time_since_last_step = 0
                        if island_num > 1:
                            off_time_since_last_step = (step['Time'].iloc[0] - laststepTime) / 3600000

                        laststepTime = step['Time'].iloc[-1]

                        island_start_row = step.index[0]
                        island_end_row = step.index[-1]

                        # ---------- Calculate Average Spike Length Percentage per Island ---------- #

                        # Convert gear positions to numerical values
                        gear_map = {"N": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6}
                        step['Current_gear_shift_position'].replace(gear_map, inplace=True)

                        # Convert to numeric and handle errors
                        step['Current_gear_shift_position'] = pd.to_numeric(
                            step['Current_gear_shift_position'], errors='coerce')

                        # Drop rows with NaN gear positions
                        step.dropna(subset=['Current_gear_shift_position'], inplace=True)

                        # Filter out rows with zero or negative engine speed and vehicle speed
                        step = step[(step['Engine_speed'] > 0) & (step['Vehicle_Speed'] > 0)]

                        # Reset index after filtering
                        step.reset_index(drop=True, inplace=True)

                        # Skip if step is too short after filtering
                        if len(step) < 2:
                            continue

                        # Calculate gear ratio
                        step['gear_ratio'] = step['Vehicle_Speed'] / step['Engine_speed']

                        # Calculate baseline gear ratio for each gear position
                        baseline_ratios = step.groupby('Current_gear_shift_position')['gear_ratio'].median()
                        step['baseline_ratio'] = step['Current_gear_shift_position'].map(baseline_ratios)

                        # Identify gear shifts
                        step['gear_shift'] = step['Current_gear_shift_position'].diff().ne(0)

                        # Get indices where gear shifts occur
                        gear_shift_indices = step.index[step['gear_shift']].tolist()

                        # Initialize list to store spike lengths
                        spike_lengths = []
                        threshold = 5  # Spike length percentage threshold
                        window_size = 5  # Number of rows before and after the gear shift

                        # Analyze spikes around each gear shift
                        for idx in gear_shift_indices:
                            if idx == 0 or idx >= len(step) - 1:
                                continue  # Skip if index is out of bounds

                            from_gear = step.loc[idx - 1, 'Current_gear_shift_position']
                            to_gear = step.loc[idx, 'Current_gear_shift_position']

                            # Define the window around the gear shift
                            start_idx = max(idx - window_size, 0)
                            end_idx = min(idx + window_size, len(step) - 1)
                            window_df = step.loc[start_idx:end_idx].copy()

                            # Calculate deviations from baseline for the window
                            window_df['deviation_from_baseline'] = np.abs(
                                window_df['gear_ratio'] - window_df['baseline_ratio'])

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

                            # Check if the spike meets the threshold criteria
                            if spike_length_percentage >= threshold:
                                spike_lengths.append(spike_length_percentage)

                        # Calculate average spike length percentage for the island
                        if spike_lengths:
                            average_spike_length_percentage = np.mean(spike_lengths)
                        else:
                            average_spike_length_percentage = 0  # Or np.nan, depending on your preference

                        # ---------- End of Spike Calculation ---------- #

                        # Calculate average_load_hp for the island
                        average_load_hp = step['load_hp'].mean()

                        # Prepare the row to append to the DataFrame
                        row = [
                            file_name, island_num, step_time, km, step_fuel,
                            step_fuel / (km / 100) if km > 0 else 0, speed_std,
                            speed_max, speed_avg, Clutch_torque, step['acceleration'].mean(),
                            step['acceleration'].std(), step['deceleration'].mean(), step['deceleration'].std(),
                            step['Engine_speed'].mean(), step['Accelerator_pedal_position'].mean(),
                            step['Accelerator_pedal_position'].std(), step['Engine_speed'].std(),
                            step['Battery_voltage'].mean(), step['Current_gear_shift_position'].mean(),
                            step['Throttle_position'].mean(), island_start_row, island_end_row, IDLE_percentage,
                            average_spike_length_percentage,
                            average_load_hp  # Added average_load_hp
                        ]

                        dff.loc[len(dff.index)] = row
                        island_num += 1
            except Exception as ex:
                print(f"Error processing file {file_path}: {ex}\n")

    try:
        dff.loc['total', 'Island_time'] = dff['Island_time'].sum()
        dff.loc['total', 'Island_distance'] = dff['Island_distance'].sum()
        dff.loc['total', 'Island_fuel_consumption'] = dff['Island_fuel_consumption'].sum()
        dff.loc['total', 'fuel_consumption_mean'] = (
            100 * dff.loc['total', 'Island_fuel_consumption'] / dff.loc['total', 'Island_distance']
            if dff.loc['total', 'Island_distance'] > 0 else 0
        )
        dff.loc['total', 'average_load_hp'] = dff['average_load_hp'].mean()  # Calculate total average_load_hp

        # Save the DataFrame to an Excel file
        dff.to_excel("data_report9_" + os.path.basename(address) + ".xlsx")
    except Exception as ex:
        print(f"Error during final aggregation or saving: {ex}")
