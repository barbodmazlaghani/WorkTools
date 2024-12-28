import pandas as pd
import os
import numpy as np

DISTANCE_DIVIDE_AMOUNT = 2
MIN_TRIP_DISTANCE = 1

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

    columns = ['file_name', 'Trip_number', 'Trip_time', 'Trip_distance', 'Trip_fuel_consumption',
               'fuel_consumption_mean', "speed_std", "speed_max", "speed_mean", "clutch_torque_mean",
               "acceleration_mean",
               "acceleration_std", "deceleration_mean", "deceleration_std", "engine_speed_mean",
               "accelerator_pedal_position_mean", "accelerator_pedal_position_std", "engine_speed_std",
               "battery_voltage_mean",
               "current_gear_shift_position_mean", "throttle_position_mean", "trip_start_index", "trip_end_index",
               "IDLE_percentage", "average_spike_length_percentage"]  # Added "average_spike_length_percentage"

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
                print(file_path)
                df = None
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)

                group_offset = 0
                df.drop(0, inplace=True)
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

                input_columns = ['Time', 'Trip_fuel_consumption', 'Vehicle_Speed', 'Engine_speed',
                                 'Accelerator_pedal_position', 'Clutch_torque', 'Cumulative_mileage',
                                 'Battery_voltage', 'Current_gear_shift_position', 'Throttle_position']
                for col in input_columns:
                    if col not in df.columns:
                        df[col] = np.nan
                if not create_file:
                    df = df[input_columns]
                    df = df.astype(float)
                else:
                    for col in input_columns:
                        df[col] = df[col].astype(float)

                # Identify trips based on engine speed
                df['trip'] = (df['Engine_speed'] != 0).astype(int).diff().replace(-1, 0).cumsum()
                df = df[df['Engine_speed'] > 0]

                # Replace invalid gear positions
                df['Current_gear_shift_position'].replace({13: 0, 14: 0}, inplace=True)
                df['time_diff'] = df['Time'].diff().abs()
                trips_folder = file_path.split('\\')[-1] + "_steps"
                if create_file:
                    try:
                        os.mkdir(trips_folder)
                    except:
                        pass
                file_name = "\\".join(file_path.split('\\')[-2:])
                # Processing each trip
                laststepTime = 0
                trip_num = 1
                for _, trip in df.groupby('trip'):
                    if DIVIDE_BY_KM:
                        step_list = divide_driver_step_by_km(trip, DISTANCE_DIVIDE_AMOUNT, group_offset)
                    else:
                        step_list = [trip]
                    step_num = 0
                    for step in step_list:
                        if len(step) < 2:
                            continue
                        km = step['Cumulative_mileage'].iloc[-1] - step['Cumulative_mileage'].iloc[0]
                        if km < MIN_TRIP_DISTANCE:
                            continue
                        step.loc[step.index[0], 'time_diff'] = 0

                        # Calculate trip time
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
                        step['time_diff'] = step['Time'].diff() / 1000
                        step['acceleration'] = step['Vehicle_Speed'].diff() / (3.6 * step['time_diff'])
                        step['deceleration'] = step.loc[step['acceleration'] < 0, 'acceleration'].abs()
                        step.loc[step['acceleration'] < 0, 'acceleration'] = np.nan

                        # Calculate IDLE_percentage
                        idle_count = len(step[(step['Engine_speed'] != 0) & (step['Vehicle_Speed'] == 0)])
                        total_count = len(step)
                        IDLE_percentage = (idle_count / total_count) * 100 if total_count > 0 else 0

                        off_time_since_last_step = 0
                        if trip_num > 0:
                            off_time_since_last_step = (step['Time'].iloc[0] - laststepTime) / 3600000

                        laststepTime = step['Time'].iloc[-1]

                        trip_start_index = step.index[0]
                        trip_end_index = step.index[-1]

                        # ---------- Calculate Average Spike Length Percentage per Trip ---------- #

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

                        # Calculate average spike length percentage for the trip
                        if spike_lengths:
                            average_spike_length_percentage = np.mean(spike_lengths)
                        else:
                            average_spike_length_percentage = 0  # Or np.nan, depending on your preference

                        # ---------- End of Spike Calculation ---------- #

                        # Prepare the row to append to the DataFrame
                        row = [
                            file_name, trip_num, step_time, km, step_fuel, step_fuel / (km / 100), speed_std,
                            speed_max, speed_avg, Clutch_torque, step['acceleration'].mean(),
                            step['acceleration'].std(), step['deceleration'].mean(), step['deceleration'].std(),
                            step['Engine_speed'].mean(), step['Accelerator_pedal_position'].mean(),
                            step['Accelerator_pedal_position'].std(), step['Engine_speed'].std(),
                            step['Battery_voltage'].mean(), step['Current_gear_shift_position'].mean(),
                            step['Throttle_position'].mean(), trip_start_index, trip_end_index, IDLE_percentage,
                            average_spike_length_percentage  # Added average_spike_length_percentage
                        ]

                        dff.loc[len(dff.index)] = row
                        trip_num += 1
                log_count += 1
                print("")
            except Exception as ex:
                print("Error:", ex, "\n")

    try:
        dff.loc['total', 'Trip_time'] = dff['Trip_time'].sum()
        dff.loc['total', 'Trip_distance'] = dff['Trip_distance'].sum()
        dff.loc['total', 'Trip_fuel_consumption'] = dff['Trip_fuel_consumption'].sum()
        dff.loc['total', 'fuel_consumption_mean'] = 100 * dff.loc['total', 'Trip_fuel_consumption'] / dff.loc[
            'total', 'Trip_distance']

        # Save the DataFrame to an Excel file
        dff.to_excel("data_report7_" + address.split('\\')[-1] + ".xlsx")
    except Exception as ex:
        print("Error:", ex)
