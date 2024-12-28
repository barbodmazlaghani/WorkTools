import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------------------
# This code provides additional context by computing total fuel consumed and total distance
# for each trip, alongside the previously computed SFC and average conditions. This can help
# explain scenarios where Rira shows better SFC (indicating efficiency in converting fuel to
# work during certain operating conditions) but may still have higher overall fuel consumption
# due to covering more distance, operating longer, or driving under conditions that require
# more total fuel.
#
# Steps:
# 1. Load data for Rira and Dena.
# 2. Convert Trip_fuel_consumption from microliters to liters (as previously corrected).
# 3. Compute per-trip metrics including:
#    - Total Fuel Used (Liters)
#    - Total Distance (if cumulative mileage is available)
#    - SFC (as before)
#    - Basic info (speed, throttle, etc.)
# 4. Print out these metrics so that the user can compare total fuel consumed with SFC.
#
# After running this code, the user will provide the output, and we can interpret how Rira,
# despite having better SFC values, might end up with higher total fuel usage overall.
# ---------------------------------------------------------------------------------------

rira_filename = 'Rira.xlsx'
dena_filename = 'Dena.xlsx'
sheet_name = 'Data'

def load_data(filename, sheet):
    df = pd.read_excel(filename, sheet_name=sheet)
    time_cols = ['time', 'timestamp_received', 'timestamp']
    for c in time_cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors='coerce')
    numeric_cols = [
        'Battery_voltage', 'Fuel_level', 'Intake_manifold_absolute_pressure',
        'Throttle_position', 'Accelerator_pedal_position', 'Coolant_temperature',
        'Vehicle_Speed', 'Engine_speed', 'Target_air_fuel_ratio',
        'Current_gear_shift_position_(Current_gear)', 'Cumulative_mileage',
        'Clutch_torque', 'Trip_fuel_consumption', 'RON_factor', 'altitude',
        'latitude', 'longitude', 'satelites', 'bearing', 'angular_speed'
    ]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')
    df.dropna(how='all', inplace=True)
    if 'trip' not in df.columns:
        raise ValueError("The 'trip' column is required but not found.")
    df = df.sort_values(by=['trip','timestamp'])
    return df

df_rira = load_data(rira_filename, sheet_name)
df_dena = load_data(dena_filename, sheet_name)

# Convert microliters to liters
if 'Trip_fuel_consumption' in df_rira.columns:
    df_rira['Trip_fuel_consumption'] = df_rira['Trip_fuel_consumption'] * 1e-6
if 'Trip_fuel_consumption' in df_dena.columns:
    df_dena['Trip_fuel_consumption'] = df_dena['Trip_fuel_consumption'] * 1e-6

max_map_rira = df_rira['Intake_manifold_absolute_pressure'].max()
max_map_dena = df_dena['Intake_manifold_absolute_pressure'].max()

df_rira['Engine_Load_Percentage'] = (df_rira['Intake_manifold_absolute_pressure'] / max_map_rira) * 100.0
df_dena['Engine_Load_Percentage'] = (df_dena['Intake_manifold_absolute_pressure'] / max_map_dena) * 100.0

SEC_PER_HOUR = 3600.0

def compute_trip_metrics(subdf):
    subdf = subdf.dropna(subset=['timestamp'])
    if len(subdf) < 2:
        return pd.Series({
            'SFC': np.nan,
            'Avg_Load': np.nan,
            'Total_Fuel_Used_L': np.nan,
            'Total_Distance_km': np.nan
        })

    subdf = subdf.sort_values('timestamp')
    trip_time_h = (subdf['timestamp'].iloc[-1] - subdf['timestamp'].iloc[0]).total_seconds() / SEC_PER_HOUR

    # Fuel consumption
    if 'Trip_fuel_consumption' in subdf.columns and subdf['Trip_fuel_consumption'].notnull().any():
        fuel_start = subdf['Trip_fuel_consumption'].iloc[0]
        fuel_end = subdf['Trip_fuel_consumption'].iloc[-1]
        total_fuel_l = (fuel_end - fuel_start) if (pd.notnull(fuel_start) and pd.notnull(fuel_end)) else np.nan
    else:
        total_fuel_l = np.nan

    # Distance traveled (if cumulative_mileage is available)
    if 'Cumulative_mileage' in subdf.columns and subdf['Cumulative_mileage'].notnull().any():
        dist_start = subdf['Cumulative_mileage'].iloc[0]
        dist_end = subdf['Cumulative_mileage'].iloc[-1]
        total_dist = (dist_end - dist_start) if (pd.notnull(dist_start) and pd.notnull(dist_end)) else np.nan
    else:
        total_dist = np.nan

    # Compute SFC if possible
    if trip_time_h > 0 and total_fuel_l is not None and total_fuel_l > 0:
        if 'Clutch_torque' in subdf.columns and 'Engine_speed' in subdf.columns:
            valid_sub = subdf.dropna(subset=['Clutch_torque','Engine_speed'])
            valid_sub['Power_kW'] = valid_sub['Clutch_torque'] * (2*np.pi*(valid_sub['Engine_speed']/60))/1000.0
            mean_power = valid_sub['Power_kW'].mean()

            if pd.notnull(mean_power) and mean_power > 0:
                fuel_lph = total_fuel_l / trip_time_h
                sfc = fuel_lph / mean_power
            else:
                sfc = np.nan
        else:
            sfc = np.nan
    else:
        sfc = np.nan

    avg_load = subdf['Engine_Load_Percentage'].mean() if 'Engine_Load_Percentage' in subdf.columns else np.nan

    return pd.Series({
        'SFC': sfc,
        'Avg_Load': avg_load,
        'Total_Fuel_Used_L': total_fuel_l,
        'Total_Distance_km': total_dist
    })

def basic_info(subdf):
    return pd.Series({
        'Avg_Speed': subdf['Vehicle_Speed'].mean(),
        'Avg_Engine_Speed': subdf['Engine_speed'].mean(),
        'Avg_Throttle': subdf['Throttle_position'].mean(),
        'Avg_Pedal': subdf['Accelerator_pedal_position'].mean(),
        'Avg_Coolant': subdf['Coolant_temperature'].mean(),
        'Avg_Load': subdf['Engine_Load_Percentage'].mean()
    })

rira_metrics = df_rira.groupby('trip', group_keys=False).apply(compute_trip_metrics)
dena_metrics = df_dena.groupby('trip', group_keys=False).apply(compute_trip_metrics)

rira_info = df_rira.groupby('trip', group_keys=False).apply(basic_info)
dena_info = df_dena.groupby('trip', group_keys=False).apply(basic_info)

rira_combined = rira_info.join(rira_metrics, lsuffix='_info', rsuffix='_calc')
dena_combined = dena_info.join(dena_metrics, lsuffix='_info', rsuffix='_calc')

# Print results for Rira
print("=== RIRA Trip Analysis with Total Fuel and Distance ===")
for trip_id, row in rira_combined.iterrows():
    print(f"Trip {trip_id}:")
    print(f"  Avg Speed (km/h): {row['Avg_Speed']:.2f}" if pd.notnull(row['Avg_Speed']) else "  Avg Speed: N/A")
    print(f"  Avg Engine Speed (RPM): {row['Avg_Engine_Speed']:.0f}" if pd.notnull(row['Avg_Engine_Speed']) else "  Avg Engine Speed: N/A")
    print(f"  Avg Throttle (%): {row['Avg_Throttle']:.2f}" if pd.notnull(row['Avg_Throttle']) else "  Avg Throttle: N/A")
    print(f"  Avg Pedal (%): {row['Avg_Pedal']:.2f}" if pd.notnull(row['Avg_Pedal']) else "  Avg Pedal: N/A")
    print(f"  Avg Coolant Temp (°C): {row['Avg_Coolant']:.1f}" if pd.notnull(row['Avg_Coolant']) else "  Avg Coolant: N/A")
    print(f"  Avg Load (%): {row['Avg_Load_info']:.1f}" if pd.notnull(row['Avg_Load_info']) else "  Avg Load: N/A")
    print(f"  Total Fuel Used (L): {row['Total_Fuel_Used_L']:.6f}" if pd.notnull(row['Total_Fuel_Used_L']) else "  Total Fuel: N/A")
    print(f"  Total Distance (km): {row['Total_Distance_km']:.3f}" if pd.notnull(row['Total_Distance_km']) else "  Total Distance: N/A")
    print(f"  SFC (L/kWh): {row['SFC']:.6f}" if pd.notnull(row['SFC']) else "  SFC: N/A")
    print()

# Print results for Dena
print("=== DENA Trip Analysis with Total Fuel and Distance ===")
for trip_id, row in dena_combined.iterrows():
    print(f"Trip {trip_id}:")
    print(f"  Avg Speed (km/h): {row['Avg_Speed']:.2f}" if pd.notnull(row['Avg_Speed']) else "  Avg Speed: N/A")
    print(f"  Avg Engine Speed (RPM): {row['Avg_Engine_Speed']:.0f}" if pd.notnull(row['Avg_Engine_Speed']) else "  Avg Engine Speed: N/A")
    print(f"  Avg Throttle (%): {row['Avg_Throttle']:.2f}" if pd.notnull(row['Avg_Throttle']) else "  Avg Throttle: N/A")
    print(f"  Avg Pedal (%): {row['Avg_Pedal']:.2f}" if pd.notnull(row['Avg_Pedal']) else "  Avg Pedal: N/A")
    print(f"  Avg Coolant Temp (°C): {row['Avg_Coolant']:.1f}" if pd.notnull(row['Avg_Coolant']) else "  Avg Coolant: N/A")
    print(f"  Avg Load (%): {row['Avg_Load_info']:.1f}" if pd.notnull(row['Avg_Load_info']) else "  Avg Load: N/A")
    print(f"  Total Fuel Used (L): {row['Total_Fuel_Used_L']:.6f}" if pd.notnull(row['Total_Fuel_Used_L']) else "  Total Fuel: N/A")
    print(f"  Total Distance (km): {row['Total_Distance_km']:.3f}" if pd.notnull(row['Total_Distance_km']) else "  Total Distance: N/A")
    print(f"  SFC (L/kWh): {row['SFC']:.6f}" if pd.notnull(row['SFC']) else "  SFC: N/A")
    print()
