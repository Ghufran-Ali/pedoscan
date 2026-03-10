# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 13:00:21 2026

@author: Ghufran
"""

"""
Analyze saved foot pressure data
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data
try:
    # Try loading numpy file first
    data = np.load("foot_data.npy")
    print(f"Loaded {len(data)} frames from foot_data.npy")
except:
    # Fall back to text file
    data = []
    with open("foot_data.txt", "r") as f:
        for line in f:
            values = line.strip().split(',')
            if len(values) == 12:
                data.append(list(map(int, values)))
    data = np.array(data)
    print(f"Loaded {len(data)} frames from foot_data.txt")

if len(data) > 0:
    # Show last frame
    last_frame = data[-1]
    foot_matrix = last_frame.reshape(3, 4)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(foot_matrix, 
               cmap='jet', 
               vmin=0, 
               vmax=1023,
               annot=True,
               fmt='d',
               square=True)
    plt.title("Foot Pressure Map (Last Frame from Proteus)", fontsize=14, fontweight='bold')
    plt.show()
    
    # Show time series of all sensors
    plt.figure(figsize=(12, 6))
    for i in range(12):
        plt.plot(data[:, i], label=f'Sensor {i+1}')
    plt.xlabel("Frame Number")
    plt.ylabel("Pressure Value")
    plt.title("All Sensor Readings Over Time")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.grid(True, alpha=0.3)
    plt.show()
    
else:
    print("No data to analyze")