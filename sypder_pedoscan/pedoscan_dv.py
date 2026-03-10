# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 11:36:44 2026

@author: Ghufran
"""

# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns

# # Load the saved file
# data = []

# with open("foot_data.txt", "r") as f:
#     for line in f:
#         values = line.strip().split(',')
#         if len(values) == 12:
#             data.append(list(map(int, values)))

# data = np.array(data)

# # Show last frame
# frame = data[-1]

# # Reshape to foot matrix
# foot_matrix = frame.reshape(3,4)

# plt.figure()
# sns.heatmap(foot_matrix, cmap='jet', vmin=0, vmax=1023)
# plt.title("Foot Pressure Map (Proteus Simulation)")
# plt.show()

# import serial
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns

# ser = serial.Serial('COM21', 9600)

# plt.ion()

# while True:
#     line = ser.readline().decode().strip()
#     values = line.split(',')

#     if len(values) == 12:
#         values = list(map(int, values))
#         foot_matrix = np.array(values).reshape(3,4)

#         plt.clf()
#         sns.heatmap(foot_matrix, cmap='jet', vmin=0, vmax=1023)
#         plt.title("Live Foot Pressure Map")
#         plt.pause(0.1)
        
        
# import serial.tools.list_ports
# print([port.device for port in serial.tools.list_ports.comports()])

import serial
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time

# Configure the serial connection
try:
    # Use Serial (with capital S) not SERIAL
    ser = serial.Serial('COM21', 9600, timeout=1)
    print(f" Connected to {ser.portstr}")
    
    # Clear any initial data
    ser.reset_input_buffer()
    time.sleep(2)  # Wait for Arduino to initialize
    
except Exception as e:
    print(f" Error opening port: {e}")
    exit()

# Set up interactive plotting
plt.ion()
fig, ax = plt.subplots(figsize=(10, 8))

# Data storage for later analysis
all_data = []
frame_count = 0

print(" Waiting for data from Proteus...")
print("Press Ctrl+C to stop and save data\n")

try:
    while True:
        # Check if data is available
        if ser.in_waiting:
            # Read a line from serial
            line = ser.readline().decode().strip()
            
            # Skip empty lines or debug messages
            if not line or line.startswith("Dual"):
                continue
            
            # Split the values
            values = line.split(',')
            
            # Check if we have 12 values
            if len(values) == 12:
                try:
                    # Convert to integers
                    values = list(map(int, values))
                    
                    # Store for later
                    all_data.append(values)
                    
                    # Reshape to 3x4 matrix (foot shape)
                    foot_matrix = np.array(values).reshape(3, 4)
                    
                    # Clear the previous plot
                    ax.clear()
                    
                    # Create heatmap
                    sns.heatmap(foot_matrix, 
                               cmap='jet', 
                               vmin=0, 
                               vmax=1023,
                               annot=True,           # Show values
                               fmt='d',              # Integer format
                               square=True,          # Square cells
                               cbar_kws={'label': 'Pressure (0-1023)'},
                               ax=ax)
                    
                    # Add labels
                    ax.set_title(f"Live Foot Pressure Map - Frame {frame_count}", 
                                fontsize=14, fontweight='bold')
                    ax.set_xlabel("Toe Region →", fontsize=12)
                    ax.set_ylabel("Heel Region →", fontsize=12)
                    
                    # Update the plot
                    plt.draw()
                    plt.pause(0.01)
                    
                    frame_count += 1
                    
                    # Print progress every 10 frames
                    if frame_count % 10 == 0:
                        print(f"Received {frame_count} frames")
                        
                except ValueError as e:
                    print(f"Error converting values: {e}")
                    print(f"Raw line: {line}")
                    
except KeyboardInterrupt:
    print("\n\nStopping data collection...")
    
finally:
    # Close the serial port
    ser.close()
    print("🔌 Serial port closed")
    
    # Save data if any was collected
    if all_data:
        # Convert to numpy array
        data_array = np.array(all_data)
        print(f"Saving {len(all_data)} frames to file...")
        
        # Save as text file
        with open("foot_data.txt", "w") as f:
            for frame in all_data:
                f.write(','.join(map(str, frame)) + '\n')
        
        # Also save as numpy array for easier loading
        np.save("foot_data.npy", data_array)
        print(" Data saved to 'foot_data.txt' and 'foot_data.npy'")    
        # Show statistics
        print("\n Data Statistics:")
        print(f"   Total frames: {len(all_data)}")
        print(f"   Min pressure: {np.min(data_array)}")
        print(f"   Max pressure: {np.max(data_array)}")
        print(f"   Mean pressure: {np.mean(data_array):.2f}")
        
        # Show the last frame in a static plot
        plt.ioff()  # Turn off interactive mode
        plt.figure(figsize=(8, 6))
        
        last_frame = data_array[-1].reshape(3, 4)
        sns.heatmap(last_frame, 
                   cmap='jet', 
                   vmin=0, 
                   vmax=1023,
                   annot=True,
                   fmt='d',
                   square=True)
        plt.title("Last Recorded Foot Pressure Map", fontsize=14, fontweight='bold')
        plt.show()
        
    else:
        print("No data was collected")

# Optional: Show port list for debugging
def list_available_ports():
    """List all available serial ports"""
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    print("\nAvailable COM ports:")
    for port in ports:
        print(f"   {port.device}: {port.description}")

# Uncomment to see available ports
# list_available_ports()