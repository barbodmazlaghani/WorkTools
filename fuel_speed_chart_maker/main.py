import matplotlib
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from tkinter import Tk
from tkinter.filedialog import askdirectory

matplotlib.use('Agg')


def get_directory():
    """
    Opens a dialog for the user to select a directory.
    Returns the selected directory path.
    """
    Tk().withdraw()  # Prevents the root window from appearing
    directory = askdirectory(title='Select Directory Containing Excel Files')
    if not directory:
        print("No directory selected. Exiting.")
        exit()
    return directory


def process_excel_file(file_path, output_dir, poly_degrees=[1, 2, 3]):
    """
    Processes a single Excel file:
    - Reads the 'Report' sheet.
    - Filters trips with trip_distance > 1 km.
    - Plots trip_speed_avg vs trip_fuel_consumption_avg.
    - Fits polynomial trendlines of specified degrees.
    - Saves the plot as a PNG image.

    Parameters:
    - file_path: Path to the Excel file.
    - output_dir: Directory to save the plot.
    - poly_degrees: List of polynomial degrees for trendlines (default is [1, 2, 3]).
    """
    try:
        # Read the 'Report' sheet
        df = pd.read_excel(file_path, sheet_name='Report')
        print(f"Processing file: {os.path.basename(file_path)}")

        # Check if required columns exist
        required_columns = ['trip_distance', 'trip_speed_avg', 'trip_fuel_consumption_avg']
        if not all(col in df.columns for col in required_columns):
            print(f"Missing required columns in {os.path.basename(file_path)}. Skipping plot.")
            return

        # Ensure 'trip_distance' is numeric
        df['trip_distance'] = pd.to_numeric(df['trip_distance'], errors='coerce')

        # Filter trips with trip_distance > 1 km
        filtered_df = df[df['trip_distance'] > 1]

        if filtered_df.empty:
            print(f"No trips with trip_distance > 1 km in {os.path.basename(file_path)}. Skipping plot.")
            return

        # Ensure relevant columns are numeric
        filtered_df['trip_speed_avg'] = pd.to_numeric(filtered_df['trip_speed_avg'], errors='coerce')
        filtered_df['trip_fuel_consumption_avg'] = pd.to_numeric(filtered_df['trip_fuel_consumption_avg'],
                                                                 errors='coerce')
        filtered_df['trip_speed_avg'] = filtered_df['trip_speed_avg'].apply(lambda x: round(x / 10) * 10)

        filtered_df = filtered_df[(filtered_df['trip_speed_avg'] >= 0) & (filtered_df['trip_speed_avg'] <= 100)]
        filtered_df = filtered_df[
            (filtered_df['trip_fuel_consumption_avg'] >= 5) & (filtered_df['trip_fuel_consumption_avg'] <= 35)]

        # Drop rows with NaN values in the relevant columns
        plot_df = filtered_df.dropna(subset=['trip_speed_avg', 'trip_fuel_consumption_avg'])

        if plot_df.empty:
            print(f"No valid data to plot in {os.path.basename(file_path)}. Skipping plot.")
            return

        # Create the scatter plot
        plt.figure(figsize=(10, 6))
        plt.scatter(plot_df['trip_speed_avg'], plot_df['trip_fuel_consumption_avg'],
                    alpha=0.7, edgecolors='b', label='Trips')

        plt.xlim(0, 100)  # Limit x-axis to 0–100 for speed
        plt.ylim(0, 35)  # Limit y-axis to 5–35 for fuel consumption

        # Add titles and labels
        plt.title(f'Average Speed vs. Fuel Consumption for {os.path.basename(file_path)}\n(Trips > 1 km)')
        plt.xlabel('Average Speed (trip_speed_avg)')
        plt.ylabel('Average Fuel Consumption (trip_fuel_consumption_avg)')

        # Colors and styles for different trendlines
        trendline_styles = {
            1: {'color': 'red', 'linestyle': '--', 'label': 'Linear Trend Line (Degree 1)'},
            2: {'color': 'green', 'linestyle': '-.', 'label': 'Quadratic Trend Line (Degree 2)'},
            3: {'color': 'purple', 'linestyle': ':', 'label': 'Cubic Trend Line (Degree 3)'}
        }

        # Fit and plot each polynomial trendline
        x_min, x_max = plot_df['trip_speed_avg'].min(), plot_df['trip_speed_avg'].max()
        x_trend = np.linspace(x_min, x_max, 500)

        for degree in poly_degrees:
            # Fit the polynomial
            z = np.polyfit(plot_df['trip_speed_avg'], plot_df['trip_fuel_consumption_avg'], degree)
            p = np.poly1d(z)
            y_trend = p(x_trend)

            # Plot the trendline
            style = trendline_styles.get(degree, {})
            if degree == 2 :
                plt.plot(x_trend, y_trend, linestyle=style.get('linestyle', '--'),
                     color=style.get('color', 'black'),
                     label=style.get('label', f'Polynomial Trend Line (Degree {degree})'))

        plt.legend()
        plt.grid(True)

        # Save the plot
        excel_filename = os.path.splitext(os.path.basename(file_path))[0]
        plot_filename = f"{excel_filename}_speed_vs_fuel.png"
        plot_path = os.path.join(output_dir, plot_filename)
        plt.savefig(plot_path)
        plt.close()
        print(f"Plot saved as: {plot_filename}\n")

    except Exception as e:
        print(f"Error processing {os.path.basename(file_path)}: {e}")


def main():
    # Get directory from user
    data_dir = get_directory()

    # Create an output directory for plots
    output_dir = os.path.join(data_dir, 'Plots')
    os.makedirs(output_dir, exist_ok=True)

    # Define the degrees of the polynomials for trendlines
    polynomial_degrees = [1, 2, 3]  # Linear, Quadratic, Cubic

    # Iterate over each Excel file in the directory
    for file in os.listdir(data_dir):
        if file.endswith('.xlsx') or file.endswith('.xls'):
            file_path = os.path.join(data_dir, file)
            process_excel_file(file_path, output_dir, poly_degrees=polynomial_degrees)

    print(f"All plots have been saved in the 'Plots' folder within {data_dir}.")


if __name__ == "__main__":
    # Optional: Specify a compatible matplotlib backend if necessary
    # Uncomment the following lines if you encounter backend-related issues
    # import matplotlib
    # matplotlib.use('Agg')  # Use a non-interactive backend

    main()
