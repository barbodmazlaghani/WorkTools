import pandas as pd
import os
import numpy as np
import re

DISTANCE_DIVIDE_AMOUNT = 2
MIN_TRIP_DISTANCE = 1

DIVIDE_BY_KM = False


def divide_driver_step_by_km(df, km, group_offset):
    res = []
    df['distance_group'] = group_offset + (df['Cumulative_mileage'] - df['Cumulative_mileage'].iloc[0]) // km
    for name, df2 in df.groupby('distance_group'):
        res.append(df2)
    return res


def clean_sheet_name(name):
    """
    Cleans the sheet name by removing invalid characters and trimming to 31 characters.
    """
    # Define invalid characters for Excel sheet names
    invalid_chars = ['\\', '/', '*', '?', ':', '[', ']']
    for char in invalid_chars:
        name = name.replace(char, '_')

    # Trim the name to 31 characters (Excel's limit)
    name = name.strip()[:31]

    # If the name is empty after cleaning, assign a default name
    if not name:
        name = "Sheet"

    return name


# Initialize a dictionary to hold dataframes per driver
driver_data = {}

while True:
    columns = [
        'file_name', 'Trip_number', 'Trip_time', 'Trip_distance', 'Trip_fuel_consumption',
        'fuel_consumption_mean', "speed_std", "speed_max", "speed_mean", "clutch_torque_mean",
        "acceleration_mean", "acceleration_std", "deceleration_mean", "deceleration_std",
        "engine_speed_mean", "accelerator_pedal_position_mean", "accelerator_pedal_position_std",
        "engine_speed_std", "battery_voltage_mean", "current_gear_shift_position_mean",
        "throttle_position_mean", "trip_start_index", "trip_end_index", "IDLE_percentage"
    ]

    address = input("Enter folder address (leave empty to exit): ").strip()
    if address == '':
        break

    log_count = 0
    for root, dirs, files in os.walk(address):
        # Filter directories that start with a number
        dirs[:] = [d for d in dirs if re.match(r'^\d+', d)]

        for dir_name in dirs:
            # Extract driver name assuming format 'number_driver_other'
            parts = dir_name.split('_')
            if len(parts) < 2:
                print(f"Skipping directory '{dir_name}' as it does not conform to the expected format.")
                continue
            driver_name_raw = parts[1].strip()
            # Normalize driver name to lowercase for consistent grouping
            driver_name = driver_name_raw.lower()

            # Initialize dataframe for the driver if not already done
            if driver_name not in driver_data:
                driver_data[driver_name] = pd.DataFrame(columns=columns)

            driver_df = driver_data[driver_name]

            dir_path = os.path.join(root, dir_name)
            for file in os.listdir(dir_path):
                file_path = os.path.join(dir_path, file)
                if not os.path.isfile(file_path):
                    continue
                if file.startswith('~') or file.split('.')[-1].lower() not in ['xlsx',
                                                                               'csv'] or file.lower() == 'dtc.xlsx':
                    continue
                try:
                    print(f"Processing file: {file_path}")
                    df = None
                    if file_path.endswith('.csv'):
                        # Skip the second row (index 1) which contains units
                        df = pd.read_csv(file_path, skiprows=[1])
                    else:
                        # Skip the second row (index 1) which contains units
                        df = pd.read_excel(file_path, skiprows=[1])

                    group_offset = 0
                    # Remove any unnamed columns that might result from skipped rows
                    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                    if 'Consumed fuel' in df.columns:
                        df['Consumed fuel'] = df['Consumed fuel'].astype(float) * 1000000
                    if 'consumed fuel' in df.columns:
                        df['consumed fuel'] = df['consumed fuel'].astype(float) * 1000000

                    # Rename columns
                    df.rename(columns={
                        'Clutch_torque_(Engine_Torque)': 'Clutch_torque',
                        'Cumulative mileage': 'Cumulative_mileage',
                        'Current_gear_shift_position_(Gear_State)': 'Current_gear_shift_position_(Current_gear)',
                        'Consumed fuel': 'Trip_fuel_consumption',
                        'Total mileage of vehicle': 'Cumulative_mileage',
                        'Vehicle speed': 'Vehicle_Speed',
                        'Engine Torque': 'Clutch_torque',
                        'vehicle speed': 'Vehicle_Speed',
                        'consumed fuel': 'Trip_fuel_consumption',
                        'Battery voltage': 'Battery_voltage',
                        'current gear': 'Current_gear_shift_position_(Current_gear)',
                        'Total kilometre travelled in both gasoline and CNG mode': 'Cumulative_mileage',
                        'Engine speed': 'Engine_speed',
                        'GAS Pedal Module ( P1 & P2 )': 'Accelerator_pedal_position',
                        'throttle angle with respect to lower mechanical stop': 'Throttle_position',
                        'Normalized angle acceleration pedal': 'Accelerator_pedal_position',
                        'Battery voltage (on board), conversed to standard quantization and low pass filter': 'Battery_voltage',
                        'Engaged gear': 'Current_gear_shift_position_(Current_gear)'
                    }, inplace=True)

                    input_columns = [
                        'Time', 'Trip_fuel_consumption', 'Vehicle_Speed', 'Engine_speed',
                        'Accelerator_pedal_position', 'Clutch_torque', 'Cumulative_mileage',
                        'Battery_voltage', 'Current_gear_shift_position_(Current_gear)', 'Throttle_position'
                    ]
                    for col in input_columns:
                        if col not in df.columns:
                            df[col] = 0  # Assign 0 instead of NaN
                    if not DIVIDE_BY_KM:
                        df = df[input_columns].astype(float)
                    else:
                        for col in input_columns:
                            df[col] = df[col].astype(float)

                    df['trip'] = (df['Engine_speed'] != 0).astype(int).diff().replace(-1, 0).cumsum()
                    df = df[df['Engine_speed'] > 0]

                    df['Current_gear_shift_position_(Current_gear)'].replace([13, 14], 0, inplace=True)
                    df['time_diff'] = df['Time'].diff().abs()
                    trips_folder = os.path.join(dir_path, f"{os.path.splitext(file)[0]}_steps")
                    if DIVIDE_BY_KM:
                        os.makedirs(trips_folder, exist_ok=True)
                    file_name = os.path.join(dir_name, file)

                    # Processing each trip
                    laststepTime = 0
                    trip_num = 1
                    for _, trip in df.groupby('trip'):
                        if DIVIDE_BY_KM:
                            step_list = divide_driver_step_by_km(trip, DISTANCE_DIVIDE_AMOUNT, group_offset)
                        else:
                            step_list = [trip]
                        for step in step_list:
                            if len(step) < 2:
                                continue
                            km = step['Cumulative_mileage'].iloc[-1] - step['Cumulative_mileage'].iloc[0]
                            if km < MIN_TRIP_DISTANCE:
                                continue

                            # Avoid SettingWithCopyWarning
                            step = step.copy()
                            step.loc[step.index[0], 'time_diff'] = 0

                            step_time = step.loc[step['time_diff'] < 10000, 'time_diff'].sum() / 3600000
                            step['momentary_fuel_consumption'] = step['Trip_fuel_consumption'].diff()
                            step_fuel = step.loc[
                                            (step['momentary_fuel_consumption'] > 0) &
                                            (step['momentary_fuel_consumption'] < 199999),
                                            'momentary_fuel_consumption'
                                        ].sum() / 1000000

                            speed_avg = step['Vehicle_Speed'].mean()
                            speed_std = step['Vehicle_Speed'].std()
                            speed_max = step['Vehicle_Speed'].max()
                            Clutch_torque = step['Clutch_torque'].mean()

                            step['time_diff'] = step['Time'].diff() / 1000
                            step['acceleration'] = step['Vehicle_Speed'].diff() / (3.6 * step['time_diff'])
                            step['deceleration'] = step['acceleration'].where(step['acceleration'] < 0, np.nan).abs()

                            # Calculate IDLE_percentage
                            idle_count = len(step[(step['Engine_speed'] != 0) & (step['Vehicle_Speed'] == 0)])
                            total_count = len(step)
                            IDLE_percentage = (idle_count / total_count) * 100 if total_count > 0 else 0

                            off_time_since_last_step = 0
                            if trip_num > 1:
                                off_time_since_last_step = (step['Time'].iloc[0] - laststepTime) / 3600000

                            laststepTime = step['Time'].iloc[-1]

                            trip_start_index = step.index[0]
                            trip_end_index = step.index[-1]

                            row = [
                                file_name, trip_num, step_time, km, step_fuel,
                                step_fuel / (km / 100) if km > 0 else 0,  # Assign 0 instead of NaN
                                speed_std, speed_max, speed_avg, Clutch_torque,
                                step['acceleration'].mean(), step['acceleration'].std(),
                                step['deceleration'].mean(), step['deceleration'].std(),
                                step['Engine_speed'].mean(), step['Accelerator_pedal_position'].mean(),
                                step['Accelerator_pedal_position'].std(), step['Engine_speed'].std(),
                                step['Battery_voltage'].mean(),
                                step['Current_gear_shift_position_(Current_gear)'].mean(),
                                step['Throttle_position'].mean(), trip_start_index, trip_end_index, IDLE_percentage
                            ]

                            driver_df.loc[len(driver_df.index)] = row
                            trip_num += 1
                    driver_data[driver_name] = driver_df
                    log_count += 1
                    print("")
                except Exception as ex:
                    print(f"Error processing file '{file_path}': {ex}\n")

    try:
        # Create an Excel writer object
        report_filename = f"data_report_{os.path.basename(os.path.normpath(address))}.xlsx"
        with pd.ExcelWriter(report_filename, engine='xlsxwriter') as writer:
            for driver, df in driver_data.items():
                # Calculate totals for the driver
                total_trip_distance = df['Trip_distance'].sum()
                total_trip_fuel = df['Trip_fuel_consumption'].sum()
                total_trip_time = df['Trip_time'].sum()

                # Compute fuel_consumption_mean safely
                if total_trip_distance > 0:
                    fuel_consumption_mean = 100 * total_trip_fuel / total_trip_distance
                else:
                    fuel_consumption_mean = 0  # Assign 0 instead of np.nan

                totals = {
                    'Trip_time': total_trip_time,
                    'Trip_distance': total_trip_distance,
                    'Trip_fuel_consumption': total_trip_fuel,
                    'fuel_consumption_mean': fuel_consumption_mean
                }
                # Create a DataFrame for totals
                total_df = pd.DataFrame(totals, index=['total'])

                # Append totals to the driver's dataframe
                df_with_totals = pd.concat([df, total_df], ignore_index=False)

                # Replace any remaining NaNs with 0
                df_with_totals.fillna(0, inplace=True)

                # Generate a cleaned sheet name (e.g., capitalize first letter)
                cleaned_driver_name = driver.capitalize()
                unique_sheet_name = clean_sheet_name(cleaned_driver_name)

                # Write to a separate sheet for each driver
                df_with_totals.to_excel(writer, sheet_name=unique_sheet_name, index=False)
        print(f"Report successfully saved as '{report_filename}'")
    except Exception as ex:
        print(f"Error generating report: {ex}")
