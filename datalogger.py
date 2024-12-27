import serial
import matplotlib.pyplot as plt
import time
import csv
import os
from serial.tools import list_ports


def get_serial_data(port='COM4', baudrate=9600, identifier1="A2:", identifier2="A3:", filename="sensor_data.csv"):
    """
    Reads voltage data from a serial port, yields it, and stores it in a CSV file.

    Args:
        port (str, optional): The serial port to use. Defaults to 'COM4'.
        baudrate (int, optional): The baud rate. Defaults to 9600.
        identifier1 (str, optional): The identifier for the first voltage value.
                                       Defaults to "A2:".
        identifier2 (str, optional): The identifier for the second voltage value.
                                       Defaults to "A3:".
        filename (str, optional): The name of the CSV file to store the data.
                                   Defaults to "sensor_data.csv".
    """

    try:
        with serial.Serial(port, baudrate) as ser, open(filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # Write header if the file is empty
            if csvfile.tell() == 0:
                writer.writerow(["Timestamp", "A2 Voltage", "A3 Voltage"])

            timestamps = []
            voltage1_values = []
            voltage2_values = []
            start_time = time.time()

            while True:
                line = ser.readline().decode().strip()
                print(f"DEBUG: {line}")

                try:
                    if line.startswith(identifier1):
                        voltage1_values.append(float(line.split(":")[1]))
                    elif line.startswith(identifier2):
                        voltage2_values.append(float(line.split(":")[1]))
                        timestamps.append(time.time() - start_time)

                    if len(voltage1_values) == len(voltage2_values):
                        # Write data to CSV
                        for i in range(len(timestamps)):
                            writer.writerow([timestamps[i], voltage1_values[i], voltage2_values[i]])
                        print(f"Data appended to {filename}")

                        yield timestamps, voltage1_values, voltage2_values

                except (ValueError, IndexError) as e:
                    print(f"Error parsing: {e}")

    except serial.SerialException as e:
        print(f"Serial port error: {e}")
    except Exception as e:
        print(f"Error storing data: {e}")



def plot_data(data_generator):
    """Plots voltage data in real-time."""

    plt.ion()
    fig, ax = plt.subplots()
    line1, = ax.plot([], [], 'r-', label='A2 Voltage')
    line2, = ax.plot([], [], 'b-', label='A3 Voltage')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Voltage (V)')
    ax.legend()

    for timestamps, voltage1_values, voltage2_values in data_generator:
        line1.set_data(timestamps, voltage1_values)
        line2.set_data(timestamps, voltage2_values)
        ax.relim()
        ax.autoscale_view()
        fig.canvas.draw()
        fig.canvas.flush_events()
        plt.pause(0.01)



if __name__ == "__main__":
    data_generator = get_serial_data(identifier1="A2:", identifier2="A3:")

    try:
        for timestamps, voltage1_values, voltage2_values in data_generator:
            plot_data(data_generator)  # Update the plot
            time.sleep(1)  # Adjust the interval as needed

    except KeyboardInterrupt:
        print("Exiting...")
        plt.ioff()  # Turn off interactive mode
        plt.show()  # Show the plot (blocking)