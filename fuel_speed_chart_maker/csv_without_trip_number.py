import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk
from tkinter.filedialog import askdirectory
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')

def add_trip_numbers(file_path):
    """
    Adds trip numbers to the given CSV file.
    """
    df = pd.read_csv(file_path, low_memory=False)
    df = df.drop(0).reset_index(drop=True)

    # Check if required columns exist
    required_columns = ['Engine_speed', 'Battery_voltage','Cumulative_mileage','Trip_fuel_consumption']
    if not all(col in df.columns for col in required_columns):
        print(f"One of the required columns {required_columns} not found in {file_path}. Skipping this file.")
        return None
    df['Engine_speed'] = pd.to_numeric(df['Engine_speed'], errors='coerce')
    df['Battery_voltage'] = pd.to_numeric(df['Battery_voltage'], errors='coerce')

    df['Cumulative_mileage'] = pd.to_numeric(df['Cumulative_mileage'], errors='coerce')
    df['Trip_fuel_consumption'] = pd.to_numeric(df['Trip_fuel_consumption'], errors='coerce')

    # Initialize variables for trip tracking
    trip_number = 0
    trip_numbers = []
    in_trip = False

    for _, row in df.iterrows():
        engine_speed = row['Engine_speed']
        battery_voltage = row['Battery_voltage']

        if engine_speed > 0 and battery_voltage > 0:  # Start or continue a trip
            if not in_trip:
                trip_number += 1
                in_trip = True
            trip_numbers.append(trip_number)
        else:  # End the current trip
            in_trip = False
            trip_numbers.append(0)

    df['Trip'] = trip_numbers

    df['Trip'] = pd.to_numeric(df['Trip'], errors='coerce')
    return df

def process_csv_file(file_path, poly_degrees=[2]):
    """
    Processes a CSV file to generate plots of speed vs. fuel consumption.
    """
    try:
        df = add_trip_numbers(file_path)
        if df is None:
            return

        # Save updated CSV with trip numbers
        required_columns = ['Trip', 'Vehicle_Speed', 'Trip_fuel_consumption', 'Cumulative_mileage']
        if not all(col in df.columns for col in required_columns):
            print(f"Missing required columns in {file_path}. Skipping plot.")
            return

        df['Vehicle_Speed'] = pd.to_numeric(df['Vehicle_Speed'], errors='coerce')
        df['Trip_fuel_consumption'] = pd.to_numeric(df['Trip_fuel_consumption'], errors='coerce')

        trip_stats = df.groupby('Trip').agg(
            trip_speed_avg=('Vehicle_Speed', 'mean'),
            trip_fuel_consumption_start=('Trip_fuel_consumption', 'first'),
            trip_fuel_consumption_end=('Trip_fuel_consumption', 'last'),
            mileage_start=('Cumulative_mileage', 'first'),
            mileage_end=('Cumulative_mileage', 'last')
        ).reset_index()

        trip_stats = trip_stats[trip_stats['Trip'] > 0]
        trip_stats['cumulative_mileage'] = trip_stats['mileage_end'] - trip_stats['mileage_start']



        trip_stats['trip_fuel_consumption_avg'] = (
            ((trip_stats['trip_fuel_consumption_end'] - trip_stats['trip_fuel_consumption_start']) / 1000000) /
            (trip_stats['mileage_end'] - trip_stats['mileage_start'])
        ) * 100

        trip_stats = trip_stats.dropna(subset=['trip_speed_avg', 'trip_fuel_consumption_avg'])
        trip_stats = trip_stats[trip_stats['cumulative_mileage'] > 1]
        trip_stats = trip_stats[trip_stats['trip_fuel_consumption_avg'] > 0]

        number_of_trips = trip_stats['Trip'].nunique()

        # Calculate the sum of cumulative mileage across all trips
        total_cumulative_mileage = trip_stats['cumulative_mileage'].sum()

        if trip_stats.empty:
            print(f"No valid trips to plot in {file_path}. Skipping plot.")
            return

        # Adjust speed averages to the nearest multiple of 10
        trip_stats['trip_speed_avg1'] = np.round(trip_stats['trip_speed_avg'] / 10) * 10

        plt.figure(figsize=(10, 6))

        # Scatter plot
        plt.scatter(trip_stats['trip_speed_avg1'], trip_stats['trip_fuel_consumption_avg'],
                    alpha=0.7, edgecolors='b', label='Trips')

        plt.xlim(0, 100)  # Limit x-axis to 0–100 for speed
        plt.ylim(0, 35)  # Limit y-axis to 0–35 for fuel consumption

        # Set title and axis labels
        plt.title(f'Average Speed vs. Fuel Consumption for {os.path.basename(file_path)}')
        plt.xlabel('Average Speed (km/h)')
        plt.ylabel('Average Fuel Consumption (%)')

        # Set grid and ticks every 10 units
        plt.xticks(np.arange(0, 101, 10))
        plt.yticks(np.arange(0, 36, 5))
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)

        # Trendline styles
        trendline_styles = {
            1: {'color': 'red', 'linestyle': '--', 'label': 'Linear Trend Line (Degree 1)'},
            2: {'color': 'green', 'linestyle': '-.', 'label': 'Quadratic Trend Line (Degree 2)'},
            3: {'color': 'purple', 'linestyle': ':', 'label': 'Cubic Trend Line (Degree 3)'}
        }

        # Generate trendlines
        x_min, x_max = trip_stats['trip_speed_avg'].min(), trip_stats['trip_speed_avg'].max()
        x_trend = np.linspace(x_min, x_max, 500)

        for degree in poly_degrees:
            z = np.polyfit(trip_stats['trip_speed_avg'], trip_stats['trip_fuel_consumption_avg'], degree)
            p = np.poly1d(z)
            y_trend = p(x_trend)

            style = trendline_styles.get(degree, {})
            plt.plot(x_trend, y_trend, linestyle=style.get('linestyle', '--'),
                     color=style.get('color', 'black'),
                     label=style.get('label', f'Polynomial Trend Line (Degree {degree})'))

        plt.legend()
        text = (
            f"Trip count : {number_of_trips} \n"
            f"mileage(KM) : {total_cumulative_mileage:.0f} \n"

        )
        plt.text(
            0.95, 0.05,  # x and y position in figure coordinates
            text,  # Multi-line text
            fontsize=10,
            color='gray',
            horizontalalignment='right',
            verticalalignment='bottom',
            transform=plt.gca().transAxes  # Use axes coordinates
        )

        # Save plot next to the CSV file
        csv_dir = os.path.dirname(file_path)
        csv_filename = os.path.splitext(os.path.basename(file_path))[0]
        plot_filename = f"{csv_filename}_speed_vs_fuel.png"
        plot_path = os.path.join(csv_dir, plot_filename)

        plt.savefig(plot_path)
        plt.close()
        print(f"Plot saved as: {plot_path}\n")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    folder_path = input("Enter the root folder path containing CSV files: ")

    # Walk through the root directory and subdirectories to find all CSV files
    csv_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))

    if not csv_files:
        print("No CSV files found in the specified folder or its subfolders.")
        return

    for file_path in csv_files:
        print(f"Processing: {file_path}")
        process_csv_file(file_path, poly_degrees=[2])

    print(f"All processing and plots saved near their respective CSV files.")

if __name__ == "__main__":
    main()
