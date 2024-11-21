import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.ticker import EngFormatter
import pandas as pd
import numpy as np

# Load the data
data = pd.read_csv('bms_data_charging.csv')

# Parse isotimestamps
data['HostTime'] = pd.to_datetime(data['HostTime'])

def interpolate_list(data):
    data = np.array(data)
    change_indices = np.where(data[:-1] != data[1:])[0] + 1
    interpolated = np.zeros(len(data), dtype=float)
    start = 0
    for end in change_indices:
        interpolated[start:end] = np.linspace(data[start], data[end], end-start, endpoint=False)
        start = end
    interpolated[start:] = np.linspace(data[start], data[-1], len(data) - start, endpoint=True)
    return interpolated

battery_percentage = data['BatteryPercent']
battery_percentage = interpolate_list(battery_percentage)

def plot_cells_balance(data):
    fig, ax = plt.subplots()
    ax.set_prop_cycle(color=plt.cm.viridis(np.linspace(0, 1, 16)))
    for i in range(2, 17):
        voltage_diff = data[f'Cell{i}Voltage'] - data['Cell1Voltage']
        voltage_diff = voltage_diff.rolling(40).mean()
        ax.plot(battery_percentage, voltage_diff, label=f'Cell{i}')


    ax.set_xlabel('Battery Percentage')
    ax.set_ylabel('Voltage')
    ax.legend()
    ax.yaxis.set_major_formatter(EngFormatter('V'))
    ax.grid(True)

def plot_cells_voltage(data):
    fig, ax = plt.subplots()
    ax.set_prop_cycle(color=plt.cm.viridis(np.linspace(0, 1, 16)))
    for i in range(1, 17):
        voltage = data[f'Cell{i}Voltage']
        voltage = voltage.rolling(40).mean()
        ax.plot(battery_percentage, voltage, label=f'Cell{i}')

    ax.set_xlabel('Battery Percentage')
    ax.set_ylabel('Voltage')
    ax.legend()
    ax.yaxis.set_major_formatter(EngFormatter('V'))
    ax.grid(True)

def plot_cells_temperature(data):
    fig, ax = plt.subplots()
    ax.set_prop_cycle(color=plt.cm.viridis(np.linspace(0, 1, 16)))
    for i in range(1, 4):
        temperature = data[f'CellTemperature{i}']
        temperature = temperature.rolling(40).mean()
        ax.plot(battery_percentage, temperature, label=f'Temp{i}')

    ax.set_xlabel('Battery Percentage')
    ax.set_ylabel('Temperature')
    ax.legend()
    ax.yaxis.set_major_formatter(EngFormatter('°C'))
    ax.grid(True)

plot_cells_balance(data)
plot_cells_voltage(data)
plot_cells_temperature(data)

plt.show()

