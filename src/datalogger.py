import serial
import matplotlib.pyplot as plt
import time
import csv

def get_serial_data(port='COM4', baudrate=9600, identifier1="A2:", identifier2="A3:"):
    """
    Reads voltage data from a serial port and yields it.

    Args:
        port (str, optional): The serial port to use. Defaults to 'COM4'.
        baudrate (int, optional): The baud rate. Defaults to 9600.
        identifier1 (str, optional): The identifier for the first voltage value. 
                                       Defaults to "A2:".
        identifier2 (str, optional): The identifier for the second voltage value. 
                                       Defaults to "A3:".
    """

    with serial.Serial(port, baudrate) as ser:
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
                    yield timestamps, voltage1_values, voltage2_values

            except (ValueError, IndexError) as e:
                print(f"Error parsing: {e}")

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

def store_data(timestamps, voltage1_values, voltage2_values, filename="sensor_data.csv"):
    """Stores the sensor data in a CSV file."""

    try:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Timestamp", "A2 Voltage", "A3 Voltage"])  # Write header row
            for i in range(len(timestamps)):
                writer.writerow([timestamps[i], voltage1_values[i], voltage2_values[i]])
        print(f"Data stored in {filename}")
    except Exception as e:
        print(f"Error storing data: {e}")

if __name__ == "__main__":
    data_generator = get_serial_data(identifier1="A2:", identifier2="A3:")

    try:
        for timestamps, voltage1_values, voltage2_values in data_generator:
            plot_data(data_generator)  # Update the plot
            store_data(timestamps, voltage1_values, voltage2_values)  # Store the data
            time.sleep(1)  # Adjust the interval as needed

    except KeyboardInterrupt:
        print("Exiting...")
        plt.ioff()  # Turn off interactive mode
        plt.show()  # Show the plot (blocking)