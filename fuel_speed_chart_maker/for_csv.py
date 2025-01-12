import matplotlib
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from tkinter import Tk
from tkinter.filedialog import askopenfilename

matplotlib.use('Agg')


def get_csv_file():
    """
    Opens a dialog for the user to select a CSV file.
    Returns the selected file path.
    """
    Tk().withdraw()  # Prevents the root window from appearing
    file_path = askopenfilename(title='Select a CSV File', filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        print("No file selected. Exiting.")
        exit()
    return file_path

def process_csv_file(file_path, output_dir, poly_degrees=[1, 2, 3]):
    """
    Processes a single CSV file:
    - Groups data by 'Trip' and calculates statistics for each trip.
    - Filters trips with a trip_distance > 1 km.
    - Plots average speed vs average fuel consumption for each trip.
    - Fits polynomial trendlines of specified degrees.
    - Saves the plot as a PNG image.

    Parameters:
    - file_path: Path to the CSV file.
    - output_dir: Directory to save the plot.
    - poly_degrees: List of polynomial degrees for trendlines (default is [1, 2, 3]).
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)

        print(f"Processing file: {os.path.basename(file_path)}")

        # Check if required columns exist
        required_columns = ['trip', 'Vehicle_Speed', 'Trip_fuel_consumption']
        if not all(col in df.columns for col in required_columns):
            print(f"Missing required columns in {os.path.basename(file_path)}. Skipping plot.")
            return
        print('1')
        # Ensure relevant columns are numeric
        df['Vehicle_Speed'] = pd.to_numeric(df['Vehicle_Speed'], errors='coerce')
        df['Trip_fuel_consumption'] = pd.to_numeric(df['Trip_fuel_consumption'], errors='coerce')
        print('2')
        # Group by 'Trip' and calculate statistics
        trip_stats = df.groupby('trip').agg(
            trip_speed_avg=('Vehicle_Speed', 'mean'),
            trip_fuel_consumption_start=('Trip_fuel_consumption', 'first'),
            trip_fuel_consumption_end=('Trip_fuel_consumption', 'last'),
            mileage_start=('Cumulative_mileage', 'first'),
            mileage_end=('Cumulative_mileage', 'last')
        ).reset_index()
        print('3')

        trip_stats['cumulative_mileage'] = trip_stats['mileage_end'] - trip_stats['mileage_start']

        # Calculate trip_fuel_consumption_avg
        trip_stats['trip_fuel_consumption_avg'] = (
                ((trip_stats['trip_fuel_consumption_end'] - trip_stats['trip_fuel_consumption_start'])/1000000) /
                (trip_stats['mileage_end'] - trip_stats['mileage_start'])
        ) * 100
        print('4')

        trip_stats = trip_stats.dropna(subset=[
            'trip_speed_avg',
            'trip_fuel_consumption_avg'
        ])

        trip_stats = trip_stats[trip_stats['cumulative_mileage'] > 1]
        trip_stats = trip_stats[trip_stats['trip_fuel_consumption_avg'] > 0]

        number_of_trips = trip_stats['trip'].nunique()

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
            2: {'color': 'red', 'linestyle': '-.', 'label': 'Quadratic Trend Line (Degree 2)'},
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
        print('--1')
        print(f"Error processing {os.path.basename(file_path)}: {e}")



def main():
    # Get CSV file from user
    csv_file = r"C:\Users\s_alizadehnia\Desktop\Repos\WorkTools\fuel_speed_chart_maker\data\csv\raf1_and_2_rira.csv"
    print(csv_file)
    # Create an output directory for plots
    output_dir = os.path.join(os.path.dirname(csv_file), 'Plots')
    os.makedirs(output_dir, exist_ok=True)

    # Define the degrees of the polynomials for trendlines
    polynomial_degrees = [2]  # Linear, Quadratic, Cubic

    # Process the selected CSV file
    process_csv_file(csv_file, output_dir, poly_degrees=polynomial_degrees)

    print(f"All plots have been saved in the 'Plots' folder within {os.path.dirname(csv_file)}.")


if __name__ == "__main__":
    main()