import serial
import time
import csv
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import sys

# Force a GUI backend (Important if graph isn't displaying)
import matplotlib
matplotlib.use('TkAgg')

# Serial port configuration
port = 'COM3'  # Change this to your port
baudrate = 115200

# Initialize CSV file
csv_file = open('drag_force.csv', mode='a', newline='')
csv_writer = csv.writer(csv_file)

if csv_file.tell() == 0:
    csv_writer.writerow(['Time', 'Drag Force'])
    csv_file.flush()

# Initialize real-time plot
plt.style.use('ggplot')
fig, ax = plt.subplots(figsize=(8, 5))
time_data, force_data = [], []
line, = ax.plot([], [], 'r-', linewidth=2, label='Drag Force')

ax.set_xlabel('Time (ms)', fontsize=12)
ax.set_ylabel('Drag Force (N)', fontsize=12)
ax.set_title('Real-Time Drag Force Measurement', fontsize=14)
ax.legend()
ax.grid(True, linestyle='--', alpha=0.6)

last_time = None  # Store the last known time before disconnection

# Serial connection function
def connect_serial():
    while True:
        try:
            ser = serial.Serial(port, baudrate, timeout=1)
            print("Connected to", port)
            return ser
        except serial.SerialException:
            print("Waiting for device...")
            time.sleep(2)

ser = connect_serial()

# Function to send tare command
def send_tare():
    global ser
    try:
        ser.write(b't\n')
        print("Tare command sent!")
    except serial.SerialException:
        print("Failed to send tare command.")

# Keyboard handler for tare
def on_key(event):
    if event.key == 't':
        send_tare()

fig.canvas.mpl_connect('key_press_event', on_key)

# Function to update plot
def update(frame):
    global time_data, force_data, ser, last_time

    try:
        while ser.in_waiting > 0:
            line_data = ser.readline().decode('utf-8').strip()

            if line_data:
                try:
                    time_val, force_val = map(float, line_data.split(', '))

                    # Handle Arduino reset
                    if last_time is not None and time_val < last_time:
                        print("Time reset detected. Clearing data.")
                        time_data.clear()
                        force_data.clear()

                    last_time = time_val

                    print(f"Time: {int(time_val)}, Drag Force: {force_val:.2f}")

                    csv_writer.writerow([int(time_val), force_val])
                    csv_file.flush()

                    time_data.append(int(time_val))
                    force_data.append(force_val)

                    if len(time_data) > 100:
                        time_data.pop(0)
                        force_data.pop(0)

                    line.set_xdata(time_data)
                    line.set_ydata(force_data)
                    ax.relim()
                    ax.autoscale_view()
                    ax.set_title(f"Real-Time Drag Force: {force_val:.2f} N", fontsize=14)

                except ValueError:
                    pass  # Skip malformed lines

    except serial.SerialException:
        print("Serial connection lost. Reconnecting...")
        try:
            ser.close()
        except:
            pass
        time.sleep(1)
        ser = connect_serial()

ani = animation.FuncAnimation(fig, update, interval=50)  # 50ms for smooth animation

try:
    plt.show()
except KeyboardInterrupt:
    print("Data collection stopped by user.")
finally:
    try:
        ser.close()
    except:
        pass
    csv_file.close()
