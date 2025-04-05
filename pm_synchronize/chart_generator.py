import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os


def load_data(csv_file):
    """
    Loads and preprocesses the synchronized car data.

    Parameters:
    - csv_file: Path to the CSV file.

    Returns:
    - pandas DataFrame with 'Datetime' as index.
    """
    df = pd.read_csv(csv_file)
    print(len(df))
    df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
    df = df.dropna(subset=['Datetime'])
    df.set_index('Datetime', inplace=True)
    return df


def plot_concentration_time_series(df, concentration_cols, output_dir='charts'):
    """
    Plots all specified concentration variables in a time series.

    Parameters:
    - df: pandas DataFrame with concentration data.
    - concentration_cols: List of concentration column names to plot.
    - output_dir: Directory to save the chart.
    """
    os.makedirs(output_dir, exist_ok=True)
    print(len(df))
    plt.figure(figsize=(15, 8))
    for col in concentration_cols:
        if col in df.columns:
            print("COL",len(df[col]))
            plt.plot(df.index, df[col], label=col, linewidth=1.5)
    plt.xlabel('Datetime')
    plt.ylabel('Concentration (ug/m3)')
    plt.title('Air Pollution Concentration Over Time')
    plt.legend()
    plt.grid(True)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.gcf().autofmt_xdate()
    output_path = os.path.join(output_dir, 'concentration_time_series.png')
    # plt.show()
    plt.savefig(output_path,dpi=300)
    plt.close()
    print(f"Chart saved as {output_path}")


def plot_concentration_vs_variable(df, concentration_cols, variable_col, variable_label, output_filename,
                                   color='black'):
    """
    Generic function to plot concentration parameters against a specified variable with dual y-axes.

    Parameters:
    - df: pandas DataFrame with data.
    - concentration_cols: List of concentration column names.
    - variable_col: Column name for the secondary variable.
    - variable_label: Label for the secondary y-axis.
    - output_filename: Filename for saving the plot.
    - color: Color for the secondary variable plot.
    """
    os.makedirs('charts', exist_ok=True)
    fig, ax1 = plt.subplots(figsize=(15, 8))
    for col in concentration_cols:
        if col in df.columns:
            ax1.plot(df.index, df[col], label=col, linewidth=1)
    ax1.set_xlabel('Datetime')
    ax1.set_ylabel('Concentration (ug/m3)')
    ax1.legend(loc='upper left')
    ax1.grid(True)
    if variable_col in df.columns:
        ax2 = ax1.twinx()
        ax2.plot(df.index, df[variable_col], color=color, label=variable_label, linewidth=1.5)
        ax2.set_ylabel(variable_label)
        ax2.legend(loc='upper right')
    plt.title(f'Concentration Parameters and {variable_label} Over Time')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    fig.autofmt_xdate()
    output_path = os.path.join('charts', output_filename)
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Chart saved as {output_path}")


def main():
    csv_file = 'synchronized_car_data.csv'
    df = load_data(csv_file)
    print(len(df))
    # Define concentration columns excluding 'TC [1/l]'
    concentration_cols = ['TSP [ug/m3]', 'PM10 [ug/m3]', 'PM2.5 [ug/m3]', 'PM1 [ug/m3]']

    # Chart 1: All Concentration Variables in a Time Series
    plot_concentration_time_series(df, concentration_cols)

    # Chart 2: All Concentration Parameters vs Vehicle Speed
    plot_concentration_vs_variable(
        df,
        concentration_cols=concentration_cols,
        variable_col='Vehicle_Speed',
        variable_label='Vehicle Speed (km/h)',
        output_filename='concentration_vs_speed.png',
        color='black'
    )

    # Chart 3: All Concentration Parameters vs Acceleration
    plot_concentration_vs_variable(
        df,
        concentration_cols=concentration_cols,
        variable_col='Acceleration',
        variable_label='Acceleration (m/s²)',
        output_filename='concentration_vs_acceleration.png',
        color='purple'
    )

    # Chart 4: All Concentration Parameters vs Deceleration
    plot_concentration_vs_variable(
        df,
        concentration_cols=concentration_cols,
        variable_col='Deceleration',
        variable_label='Deceleration (m/s²)',
        output_filename='concentration_vs_deceleration.png',
        color='orange'
    )

    # Chart 5: All Concentration Parameters vs Engine Speed
    plot_concentration_vs_variable(
        df,
        concentration_cols=concentration_cols,
        variable_col='Engine_speed',
        variable_label='Engine Speed (RPM)',
        output_filename='concentration_vs_engine_speed.png',
        color='green'
    )

    # Chart 6: All Concentration Parameters vs Accelerator Pedal Position
    plot_concentration_vs_variable(
        df,
        concentration_cols=concentration_cols,
        variable_col='Accelerator_pedal_position',
        variable_label='Accelerator Pedal Position (%)',
        output_filename='concentration_vs_accelerator_pedal.png',
        color='red'
    )


if __name__ == "__main__":
    main()
