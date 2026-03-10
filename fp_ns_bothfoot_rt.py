# -*- coding: utf-8 -*-
"""
Professional Foot Pressure Assessment System (Pedoscan-style)
Optimized for Large Velostat Sensors - 16 Points - Bilateral (Left & Right Feet)
Author: Ghufran
"""

import serial
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patches as mpatches
from matplotlib.path import Path
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch, Circle, Ellipse
from matplotlib.colors import LinearSegmentedColormap
import warnings
warnings.filterwarnings('ignore')

# REAL-TIME SERIAL READER (Proteus COM20 -> Python COM21)

def read_serial_frame(ser):
    try:
        line = ser.readline().decode().strip()
        values = list(map(float, line.split(',')))
        if len(values) == 32:
            return np.array(values)
    except:
        pass
    return None

# SENSOR LAYOUT (16 sensors per foot) - LARGE SIZE for Velostat

# RIGHT FOOT SENSORS (mirrored from original)
SENSORS_RIGHT = {
    #Big Toe (1 sensor)
     0: {"name": "Hallux",        "zone": "Big Toe",    "x": 0.30, "y": 0.96, "abbr": "BT", "size": 0.055},

    #Toes (4 sensors)
     1: {"name": "Toe 2",         "zone": "Toes",       "x": 0.44, "y": 0.93, "abbr": "T2", "size": 0.050},
     2: {"name": "Toe 3",         "zone": "Toes",       "x": 0.55, "y": 0.90, "abbr": "T3", "size": 0.048},
     3: {"name": "Toe 4",         "zone": "Toes",       "x": 0.66, "y": 0.86, "abbr": "T4", "size": 0.046},
     4: {"name": "Toe 5",         "zone": "Toes",       "x": 0.76, "y": 0.82, "abbr": "T5", "size": 0.044},

    #Metatarsals (4 sensors)
     5: {"name": "Met 1",         "zone": "Metatarsal", "x": 0.28, "y": 0.76, "abbr": "M1", "size": 0.060},
     6: {"name": "Met 2",         "zone": "Metatarsal", "x": 0.41, "y": 0.72, "abbr": "M2", "size": 0.058},
     7: {"name": "Met 3",         "zone": "Metatarsal", "x": 0.54, "y": 0.68, "abbr": "M3", "size": 0.056},
     8: {"name": "Met 4-5",       "zone": "Metatarsal", "x": 0.68, "y": 0.64, "abbr": "M4", "size": 0.054},

    #Midfoot / Arch (4 sensors)
     9: {"name": "Medial Arch 1", "zone": "Midfoot",    "x": 0.24, "y": 0.52, "abbr": "MA1", "size": 0.048},
    10: {"name": "Medial Arch 2", "zone": "Midfoot",    "x": 0.27, "y": 0.42, "abbr": "MA2", "size": 0.048},
    11: {"name": "Lateral Arch 1","zone": "Midfoot",    "x": 0.56, "y": 0.48, "abbr": "LA1", "size": 0.048},
    12: {"name": "Lateral Arch 2","zone": "Midfoot",    "x": 0.59, "y": 0.38, "abbr": "LA2", "size": 0.048},

    #Heel (3 sensors) 
    13: {"name": "Medial Heel",   "zone": "Heel",       "x": 0.32, "y": 0.16, "abbr": "HM", "size": 0.058},
    14: {"name": "Central Heel",  "zone": "Heel",       "x": 0.45, "y": 0.12, "abbr": "HC", "size": 0.058},
    15: {"name": "Lateral Heel",  "zone": "Heel",       "x": 0.58, "y": 0.16, "abbr": "HL", "size": 0.058},
}

# LEFT FOOT SENSORS (mirrored horizontally)
SENSORS_LEFT = {}
for idx, sensor in SENSORS_RIGHT.items():
    # Mirror the x-coordinate (1.0 - x) to flip horizontally
    mirrored_sensor = sensor.copy()
    mirrored_sensor['x'] = 1.0 - sensor['x']
    # Swap medial/lateral abbreviations for left foot
    abbr = sensor['abbr']
    if abbr == 'M1':
        mirrored_sensor['abbr'] = 'M1'  # Stays M1 (now on lateral side for left)
    elif abbr == 'M4':
        mirrored_sensor['abbr'] = 'M4'  # Stays M4 (now on medial side for left)
    elif abbr == 'MA1':
        mirrored_sensor['abbr'] = 'LA1'  # Swap medial/lateral arch
    elif abbr == 'MA2':
        mirrored_sensor['abbr'] = 'LA2'
    elif abbr == 'LA1':
        mirrored_sensor['abbr'] = 'MA1'
    elif abbr == 'LA2':
        mirrored_sensor['abbr'] = 'MA2'
    elif abbr == 'HM':
        mirrored_sensor['abbr'] = 'HL'  # Swap medial/lateral heel
    elif abbr == 'HL':
        mirrored_sensor['abbr'] = 'HM'
    else:
        mirrored_sensor['abbr'] = abbr
    SENSORS_LEFT[idx] = mirrored_sensor

ZONE_COLORS = {
    "Big Toe":    "#FF4444",
    "Toes":       "#FF8800",
    "Metatarsal": "#FFD700",
    "Midfoot":    "#44BB44",
    "Heel":       "#4488FF",
}

PRESSURE_CMAP = LinearSegmentedColormap.from_list(
    "pressure",
    ["#0a0a2e", "#1a3a8f", "#2196F3", "#00BCD4", "#4CAF50",
     "#FFEB3B", "#FF9800", "#F44336", "#B71C1C"]
)

# DATA LOADING - Now expects 32 values (16 per foot)
def load_data(filename="foot_data.txt"):
    data = []
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            try:
                values = list(map(float, line.split(',')))
                if len(values) == 32:  # 16 right + 16 left sensors
                    data.append(values)
            except:
                continue
    if not data:
        raise ValueError("No valid 32-sensor rows found in file.")
    data = np.array(data)
    print(f"Loaded {len(data)} frames | shape: {data.shape}")
    return data


def generate_sample_data(n_frames=80):
    np.random.seed(42)
    data = []
    for i in range(n_frames):
        phase = (i / n_frames) * 2 * np.pi
        heel_bias     = 0.5 + 0.5 * np.cos(phase)
        forefoot_bias = 0.5 + 0.5 * np.sin(phase)
        
        # Create array for 32 sensors (16 right + 16 left)
        frame = np.zeros(32)
        
        # RIGHT FOOT (indices 0-15)
        # 0: Big Toe (Hallux)
        frame[0] = int(380 + 260 * forefoot_bias + np.random.randint(-30, 30))
        
        # 1-4: Toes (4 sensors)
        frame[1] = int(260 + 170 * forefoot_bias + np.random.randint(-25, 25))  # T2
        frame[2] = int(220 + 140 * forefoot_bias + np.random.randint(-25, 25))  # T3
        frame[3] = int(180 + 110 * forefoot_bias + np.random.randint(-20, 20))  # T4
        frame[4] = int(140 + 80 * forefoot_bias + np.random.randint(-20, 20))   # T5
        
        # 5-8: Metatarsals (4 sensors)
        frame[5] = int(430 + 210 * forefoot_bias + np.random.randint(-40, 40))  # M1
        frame[6] = int(400 + 190 * forefoot_bias + np.random.randint(-35, 35))  # M2
        frame[7] = int(350 + 160 * forefoot_bias + np.random.randint(-30, 30))  # M3
        frame[8] = int(280 + 130 * forefoot_bias + np.random.randint(-25, 25))  # M4-5
        
        # 9-12: Midfoot / Arch (4 sensors)
        frame[9] = int(70 + 40 * np.random.random() + 15 * heel_bias)   # MA1
        frame[10] = int(65 + 35 * np.random.random() + 10 * heel_bias)  # MA2
        frame[11] = int(60 + 30 * np.random.random() + 10 * heel_bias)  # LA1
        frame[12] = int(55 + 25 * np.random.random() + 5 * heel_bias)   # LA2
        
        # 13-15: Heel (3 sensors)
        frame[13] = int(480 + 300 * heel_bias + np.random.randint(-50, 50))  # Medial Heel
        frame[14] = int(450 + 270 * heel_bias + np.random.randint(-45, 45))  # Central Heel
        frame[15] = int(400 + 240 * heel_bias + np.random.randint(-40, 40))  # Lateral Heel
        
        # LEFT FOOT (indices 16-31) - Slightly different pattern for natural asymmetry
        left_offset = 16
        # Add slight natural asymmetry (left foot typically slightly different)
        left_factor = 0.95 + 0.1 * np.random.random()
        
        # 16: Big Toe (Hallux) - Left
        frame[16] = int((380 + 260 * forefoot_bias) * left_factor + np.random.randint(-30, 30))
        
        # 17-20: Toes (4 sensors) - Left
        frame[17] = int((260 + 170 * forefoot_bias) * left_factor * 0.98 + np.random.randint(-25, 25))
        frame[18] = int((220 + 140 * forefoot_bias) * left_factor * 0.97 + np.random.randint(-25, 25))
        frame[19] = int((180 + 110 * forefoot_bias) * left_factor * 0.96 + np.random.randint(-20, 20))
        frame[20] = int((140 + 80 * forefoot_bias) * left_factor * 0.95 + np.random.randint(-20, 20))
        
        # 21-24: Metatarsals (4 sensors) - Left
        frame[21] = int((430 + 210 * forefoot_bias) * left_factor * 1.02 + np.random.randint(-40, 40))
        frame[22] = int((400 + 190 * forefoot_bias) * left_factor * 1.01 + np.random.randint(-35, 35))
        frame[23] = int((350 + 160 * forefoot_bias) * left_factor * 1.00 + np.random.randint(-30, 30))
        frame[24] = int((280 + 130 * forefoot_bias) * left_factor * 0.99 + np.random.randint(-25, 25))
        
        # 25-28: Midfoot / Arch (4 sensors) - Left
        frame[25] = int((70 + 40 * np.random.random() + 15 * heel_bias) * 0.98)
        frame[26] = int((65 + 35 * np.random.random() + 10 * heel_bias) * 0.97)
        frame[27] = int((60 + 30 * np.random.random() + 10 * heel_bias) * 0.96)
        frame[28] = int((55 + 25 * np.random.random() + 5 * heel_bias) * 0.95)
        
        # 29-31: Heel (3 sensors) - Left
        frame[29] = int((480 + 300 * heel_bias) * left_factor * 0.98 + np.random.randint(-50, 50))
        frame[30] = int((450 + 270 * heel_bias) * left_factor * 0.97 + np.random.randint(-45, 45))
        frame[31] = int((400 + 240 * heel_bias) * left_factor * 0.96 + np.random.randint(-40, 40))
        
        data.append(np.clip(frame, 0, 1023))
    return np.array(data)

# CLINICAL ANALYSIS - Now handles both feet
def analyze_feet(frame):
    # Split into right and left
    right_frame = frame[:16]
    left_frame = frame[16:]
    
    def analyze_single_foot(s, side="Right"):
        zones = {
            "Big Toe":    s[[0]],
            "Toes":       s[[1, 2, 3, 4]],
            "Metatarsal": s[[5, 6, 7, 8]],
            "Midfoot":    s[[9, 10, 11, 12]],
            "Heel":       s[[13, 14, 15]],
        }
        zone_avg = {z: np.mean(v) for z, v in zones.items()}
        zone_max = {z: np.max(v)  for z, v in zones.items()}
        zone_sum = {z: np.sum(v)  for z, v in zones.items()}
        total_sum = np.sum(s)
        zone_pct = {z: (zone_sum[z] / total_sum * 100) if total_sum > 0 else 0
                    for z in zones}

        # For right foot: medial = big toe + M1 + medial arch + medial heel
        # For left foot, medial/lateral are swapped due to mirroring
        if side == "Right":
            medial_indices = [0, 5, 9, 10, 13]
            lateral_indices = [4, 8, 11, 12, 15]
        else:  # Left foot - indices are the same but physical positions are mirrored
            medial_indices = [4, 8, 11, 12, 15]  # Now these are actually medial on left foot
            lateral_indices = [0, 5, 9, 10, 13]   # Now these are actually lateral on left foot
        
        medial  = np.mean(s[medial_indices])
        lateral = np.mean(s[lateral_indices])
        ml_ratio = medial / (lateral + 1e-6)

        forefoot = np.mean(s[[0, 1, 2, 3, 4, 5, 6, 7, 8]])
        heel     = np.mean(s[[13, 14, 15]])
        fh_ratio = forefoot / (heel + 1e-6)

        arch_avg      = zone_avg["Midfoot"]
        arch_load_pct = zone_pct["Midfoot"]

        if arch_avg < 80:
            flat_foot = "Normal Arch"
            flat_foot_risk = 0
        elif arch_avg < 150:
            flat_foot = "Mild Flat Foot"
            flat_foot_risk = 1
        elif arch_avg < 250:
            flat_foot = "Moderate Flat Foot"
            flat_foot_risk = 2
        else:
            flat_foot = "Severe Flat Foot"
            flat_foot_risk = 3

        diabetic_risk_score = 0
        diabetic_flags = []
        if s[0] > 600:  diabetic_flags.append("Hallux > 600");          diabetic_risk_score += 2
        if s[5] > 600:  diabetic_flags.append("Met 1 > 600");           diabetic_risk_score += 2
        if s[6] > 550:  diabetic_flags.append("Met 2 > 550");           diabetic_risk_score += 1
        if np.max(s[[5,6,7,8]]) > 700:
            diabetic_flags.append("Peak Metatarsal > 700");              diabetic_risk_score += 2

        if   diabetic_risk_score == 0: diabetic_risk = "Low Risk"
        elif diabetic_risk_score <= 2: diabetic_risk = "Moderate Risk"
        else:                          diabetic_risk = "High Risk"

        imbalance_flags = []
        if ml_ratio > 1.4:   imbalance_flags.append("Medial overload (Pronation)")
        elif ml_ratio < 0.7: imbalance_flags.append("Lateral overload (Supination)")
        if fh_ratio > 1.6:   imbalance_flags.append("Forefoot dominant gait")
        elif fh_ratio < 0.5: imbalance_flags.append("Heel dominant gait")
        if np.std(s[[5,6,7,8]]) > 120:
            imbalance_flags.append("Uneven metatarsal loading")

        return {
            "zones": zones, "zone_avg": zone_avg, "zone_max": zone_max,
            "zone_pct": zone_pct,
            "medial": medial, "lateral": lateral, "ml_ratio": ml_ratio,
            "forefoot": forefoot, "heel": heel, "fh_ratio": fh_ratio,
            "flat_foot": flat_foot, "flat_foot_risk": flat_foot_risk,
            "arch_load_pct": arch_load_pct,
            "diabetic_risk": diabetic_risk,
            "diabetic_risk_score": diabetic_risk_score,
            "diabetic_flags": diabetic_flags,
            "imbalance_flags": imbalance_flags,
            "max_pressure": np.max(s),
            "mean_pressure": np.mean(s),
            "total_load": np.sum(s),
        }
    
    right_res = analyze_single_foot(right_frame, "Right")
    left_res = analyze_single_foot(left_frame, "Left")
    
    return right_res, left_res


# FOOT OUTLINE (for both feet)
def draw_foot_outline(ax, x_offset=0, y_offset=0, scale=1.0, mirror=False, alpha=0.10):
    """
    Draw foot outline with optional mirroring for left foot
    """
    if mirror:
        # Mirrored version for left foot
        verts = [
            (0.50, 0.04),   # START heel center

            # Medial side going up (swapped for mirror)
            (0.42, 0.03), (0.34, 0.05), (0.28, 0.10),
            (0.22, 0.16), (0.18, 0.24), (0.20, 0.34),
            (0.21, 0.42), (0.20, 0.50), (0.20, 0.58),
            (0.20, 0.64), (0.18, 0.68), (0.18, 0.72),
            (0.18, 0.75), (0.20, 0.78), (0.22, 0.80),

            # Toe bases (scalloped edge across forefoot)
            (0.24, 0.81), (0.26, 0.80), (0.28, 0.80),
            (0.30, 0.80), (0.32, 0.79), (0.34, 0.79),
            (0.38, 0.79), (0.42, 0.79), (0.46, 0.80),
            (0.50, 0.81), (0.56, 0.83), (0.62, 0.85),
            (0.68, 0.87), (0.73, 0.87), (0.76, 0.84),

            # Lateral side going down
            (0.78, 0.80), (0.79, 0.75), (0.78, 0.70),
            (0.78, 0.64), (0.78, 0.56), (0.78, 0.48),
            (0.80, 0.42), (0.80, 0.36), (0.78, 0.30),
            (0.76, 0.22), (0.74, 0.14), (0.68, 0.08),
            (0.62, 0.04), (0.56, 0.03), (0.50, 0.04),  # back to start
        ]
        
        # Mirrored toe definitions
        toe_defs = [
            (0.70, 0.935, 0.075, 0.062),  # Hallux (now on right side for left foot)
            (0.54, 0.915, 0.052, 0.048),  # Toe 2
            (0.42, 0.885, 0.046, 0.042),  # Toe 3
            (0.32, 0.855, 0.040, 0.036),  # Toe 4
            (0.23, 0.825, 0.035, 0.030),  # Toe 5
        ]
    else:
        # Original right foot
        verts = [
            (0.50, 0.04),   # START heel center

            # Lateral side going up
            (0.58, 0.03), (0.66, 0.05), (0.72, 0.10),
            (0.78, 0.16), (0.82, 0.24), (0.80, 0.34),
            (0.79, 0.42), (0.80, 0.50), (0.80, 0.58),
            (0.80, 0.64), (0.82, 0.68), (0.82, 0.72),
            (0.82, 0.75), (0.80, 0.78), (0.78, 0.80),

            # Toe bases (scalloped edge across forefoot)
            (0.76, 0.81), (0.74, 0.80), (0.72, 0.80),
            (0.70, 0.80), (0.68, 0.79), (0.66, 0.79),
            (0.62, 0.79), (0.58, 0.79), (0.54, 0.80),
            (0.50, 0.81), (0.44, 0.83), (0.38, 0.85),
            (0.32, 0.87), (0.27, 0.87), (0.24, 0.84),

            # Medial side going down
            (0.22, 0.80), (0.21, 0.75), (0.22, 0.70),
            (0.22, 0.64), (0.22, 0.56), (0.22, 0.48),
            (0.20, 0.42), (0.20, 0.36), (0.22, 0.30),
            (0.24, 0.22), (0.26, 0.14), (0.32, 0.08),
            (0.38, 0.04), (0.44, 0.03), (0.50, 0.04),  # back to start
        ]
        
        toe_defs = [
            (0.30, 0.935, 0.075, 0.062),  # Hallux
            (0.46, 0.915, 0.052, 0.048),  # Toe 2
            (0.58, 0.885, 0.046, 0.042),  # Toe 3
            (0.68, 0.855, 0.040, 0.036),  # Toe 4
            (0.77, 0.825, 0.035, 0.030),  # Toe 5
        ]

    # Apply scaling and offset
    scaled_verts = [(x * scale + x_offset, y * scale + y_offset) for x, y in verts]
    
    codes = [Path.MOVETO] + [Path.CURVE4] * (len(scaled_verts) - 1)
    assert (len(scaled_verts) - 1) % 3 == 0, "CURVE4 vert count error"

    path = Path(scaled_verts, codes)
    body_patch = patches.PathPatch(
        path, facecolor='#f3e3c3', edgecolor='#8B6914',
        lw=1.5, alpha=alpha, zorder=0
    )
    ax.add_patch(body_patch)

    # Toe ellipses
    toe_patches = []
    for (cx, cy, rx, ry) in toe_defs:
        ellipse = Ellipse(
            (cx * scale + x_offset, cy * scale + y_offset), 
            width=rx * 2 * scale, height=ry * 2 * scale,
            facecolor='#f3e3c3', edgecolor='#8B6914',
            lw=1.5, alpha=alpha, zorder=0
        )
        ax.add_patch(ellipse)
        toe_patches.append(ellipse)

    return body_patch, toe_patches

# from matplotlib.patches import Ellipse, PathPatch
# from matplotlib.path import Path

# def draw_foot_outline(ax, x_offset=0, y_offset=0, scale=1.0, mirror=False, alpha=0.15):
#     """
#     Draw a realistic human foot sole outline with separate toes.
#     Mirror=True for left foot, False for right foot.
#     """
#     if mirror:
#         # --- LEFT FOOT ---
#         verts = [
#             # Heel center to medial side
#             (0.50, 0.04), (0.42, 0.03), (0.35, 0.05), (0.28, 0.10),
#             (0.22, 0.18), (0.20, 0.28), (0.19, 0.38), (0.20, 0.48),
#             (0.22, 0.58), (0.25, 0.68), (0.28, 0.75), (0.32, 0.80),
#             # Forefoot curve
#             (0.37, 0.83), (0.42, 0.85), (0.48, 0.86),
#             # Lateral side down to heel
#             (0.55, 0.85), (0.60, 0.83), (0.65, 0.80), (0.68, 0.75),
#             (0.71, 0.68), (0.73, 0.58), (0.74, 0.48), (0.73, 0.38),
#             (0.71, 0.28), (0.68, 0.18), (0.62, 0.10), (0.55, 0.05),
#             (0.50, 0.04)
#         ]
#         toe_defs = [
#             (0.72, 0.92, 0.075, 0.062),  # Hallux
#             (0.58, 0.90, 0.052, 0.048),  # Toe 2
#             (0.46, 0.88, 0.046, 0.042),  # Toe 3
#             (0.36, 0.85, 0.040, 0.036),  # Toe 4
#             (0.28, 0.82, 0.035, 0.030),  # Toe 5
#         ]
#     else:
#         # --- RIGHT FOOT ---
#         verts = [
#             # Heel center to lateral side
#             (0.50, 0.04), (0.58, 0.03), (0.65, 0.05), (0.72, 0.10),
#             (0.78, 0.18), (0.80, 0.28), (0.81, 0.38), (0.80, 0.48),
#             (0.78, 0.58), (0.75, 0.68), (0.72, 0.75), (0.68, 0.80),
#             # Forefoot curve
#             (0.63, 0.83), (0.58, 0.85), (0.52, 0.86),
#             # Medial side down to heel
#             (0.45, 0.85), (0.40, 0.83), (0.35, 0.80), (0.32, 0.75),
#             (0.29, 0.68), (0.27, 0.58), (0.26, 0.48), (0.27, 0.38),
#             (0.29, 0.28), (0.32, 0.18), (0.38, 0.10), (0.45, 0.05),
#             (0.50, 0.04)
#         ]
#         toe_defs = [
#             (0.28, 0.92, 0.075, 0.062),  # Hallux
#             (0.42, 0.90, 0.052, 0.048),  # Toe 2
#             (0.54, 0.88, 0.046, 0.042),  # Toe 3
#             (0.64, 0.85, 0.040, 0.036),  # Toe 4
#             (0.72, 0.82, 0.035, 0.030),  # Toe 5
#         ]

#     # Scale and offset
#     scaled_verts = [(x*scale + x_offset, y*scale + y_offset) for x,y in verts]

#     # Path for the foot outline
#     codes = [Path.MOVETO] + [Path.CURVE4]*(len(scaled_verts)-1)
#     path = Path(scaled_verts, codes)
#     body_patch = PathPatch(path, facecolor='#f3e3c3', edgecolor='#8B6914', lw=1.5, alpha=alpha, zorder=0)
#     ax.add_patch(body_patch)

#     # Draw toes as ellipses
#     toe_patches = []
#     for cx, cy, rx, ry in toe_defs:
#         ellipse = Ellipse(
#             (cx*scale + x_offset, cy*scale + y_offset),
#             width=rx*2*scale, height=ry*2*scale,
#             facecolor='#f3e3c3', edgecolor='#8B6914', lw=1.5, alpha=alpha, zorder=0
#         )
#         ax.add_patch(ellipse)
#         toe_patches.append(ellipse)

#     return body_patch, toe_patches

def pressure_to_color(value, vmin=0, vmax=1023):
    norm = np.clip((value - vmin) / (vmax - vmin), 0, 1)
    return PRESSURE_CMAP(norm)

# MAIN HEATMAP VISUALIZATION - Now with both feet
def plot_heatmap(frame_idx=-1, data=None, save=True):
    if data is None:
        raise ValueError("Pass data array.")
    if frame_idx == -1:
        frame_idx = len(data) - 1
    frame = data[frame_idx]
    right_res, left_res = analyze_feet(frame)
    
    # Split frame data
    right_frame = frame[:16]
    left_frame = frame[16:]

    # Figure layout - adjusted to better center the foot maps
    fig = plt.figure(figsize=(24, 13), facecolor='#0d1117')
    gs = GridSpec(3, 5, figure=fig,
                  left=0.05, right=0.95, top=0.92, bottom=0.05,
                  wspace=0.25, hspace=0.40,
                  width_ratios=[0.8, 1.2, 1.2, 0.8, 0.8])  # Reduced left empty column width

    #Panel 1: LEFT FOOT Heatmap
    ax_left = fig.add_subplot(gs[:, 1])
    ax_left.set_facecolor('#0d1117')
    ax_left.set_xlim(0, 1)
    ax_left.set_ylim(0, 1.08)
    ax_left.set_aspect('equal')
    ax_left.axis('off')
    ax_left.set_title("LEFT FOOT PRESSURE MAP", color='#FFD700', fontsize=13,
                       fontweight='bold', y=0.96)

    #Build heatmap for left foot
    grid_size = 300
    xs = np.linspace(0, 1, grid_size)
    ys = np.linspace(0, 1.08, grid_size)
    XX, YY = np.meshgrid(xs, ys)

    vmax_left = max(np.max(left_frame), 1)
    heatmap_left = np.zeros((grid_size, grid_size))
    for idx, sinfo in SENSORS_LEFT.items():
        val = left_frame[idx]
        sx, sy = sinfo['x'], sinfo['y']
        sigma = 0.06
        blob = np.exp(-((XX - sx)**2 + (YY - sy)**2) / (2 * sigma**2))
        heatmap_left += blob * val

    heatmap_left_norm = heatmap_left / (np.max(heatmap_left) + 1e-6)

    #Draw left foot outline
    body_patch_left, toe_patches_left = draw_foot_outline(ax_left, mirror=True, alpha=0.12)

    #Left foot heatmap
    im_left = ax_left.imshow(
        heatmap_left_norm,
        origin='lower',
        extent=[0, 1, 0, 1.08],
        cmap=PRESSURE_CMAP,
        alpha=0.88,
        vmin=0, vmax=1,
        zorder=2,
        aspect='auto'
    )
    im_left.set_clip_path(body_patch_left)

    #Toe heatmaps
    for toe_patch in toe_patches_left:
        im_toe = ax_left.imshow(
            heatmap_left_norm,
            origin='lower',
            extent=[0, 1, 0, 1.08],
            cmap=PRESSURE_CMAP,
            alpha=0.88,
            vmin=0, vmax=1,
            zorder=2,
            aspect='auto'
        )
        im_toe.set_clip_path(toe_patch)

    #Redraw outline
    draw_foot_outline(ax_left, mirror=True, alpha=0.30)

    #Left foot sensor dots
    for idx, sinfo in SENSORS_LEFT.items():
        val = left_frame[idx]
        norm_val = val / vmax_left
        col = pressure_to_color(val, 0, vmax_left)

        base_size = sinfo.get('size', 0.050)
        r = base_size * (0.9 + 0.2 * norm_val)
        
        circle = plt.Circle((sinfo['x'], sinfo['y']), r,
                              color=col, alpha=0.92,
                              ec='white', linewidth=2.0, zorder=5)
        ax_left.add_patch(circle)

        ax_left.text(sinfo['x'], sinfo['y'], sinfo['abbr'],
                     ha='center', va='center', fontsize=10,
                     fontweight='bold', color='white', zorder=6,
                     bbox=dict(boxstyle='round,pad=0.2', facecolor='#000000', alpha=0.6))
        
        ax_left.text(sinfo['x'], sinfo['y'] - r - 0.030, f"{int(val)}",
                     ha='center', va='top', fontsize=8,
                     color='#ffffff', fontweight='bold', zorder=6)

    #Panel 2: RIGHT FOOT Heatmap
    ax_right = fig.add_subplot(gs[:, 2])
    ax_right.set_facecolor('#0d1117')
    ax_right.set_xlim(0, 1)
    ax_right.set_ylim(0, 1.08)
    ax_right.set_aspect('equal')
    ax_right.axis('off')
    ax_right.set_title("RIGHT FOOT PRESSURE MAP", color='#FFD700', fontsize=13,
                        fontweight='bold', y=0.96)

    #Build heatmap for right foot
    vmax_right = max(np.max(right_frame), 1)
    heatmap_right = np.zeros((grid_size, grid_size))
    for idx, sinfo in SENSORS_RIGHT.items():
        val = right_frame[idx]
        sx, sy = sinfo['x'], sinfo['y']
        sigma = 0.06
        blob = np.exp(-((XX - sx)**2 + (YY - sy)**2) / (2 * sigma**2))
        heatmap_right += blob * val

    heatmap_right_norm = heatmap_right / (np.max(heatmap_right) + 1e-6)

    #Draw right foot outline
    body_patch_right, toe_patches_right = draw_foot_outline(ax_right, mirror=False, alpha=0.12)

    #Right foot heatmap
    im_right = ax_right.imshow(
        heatmap_right_norm,
        origin='lower',
        extent=[0, 1, 0, 1.08],
        cmap=PRESSURE_CMAP,
        alpha=0.88,
        vmin=0, vmax=1,
        zorder=2,
        aspect='auto'
    )
    im_right.set_clip_path(body_patch_right)

    #Toe heatmaps
    for toe_patch in toe_patches_right:
        im_toe = ax_right.imshow(
            heatmap_right_norm,
            origin='lower',
            extent=[0, 1, 0, 1.08],
            cmap=PRESSURE_CMAP,
            alpha=0.88,
            vmin=0, vmax=1,
            zorder=2,
            aspect='auto'
        )
        im_toe.set_clip_path(toe_patch)

    #Redraw outline
    draw_foot_outline(ax_right, mirror=False, alpha=0.30)

    #Right foot sensor dots
    for idx, sinfo in SENSORS_RIGHT.items():
        val = right_frame[idx]
        norm_val = val / vmax_right
        col = pressure_to_color(val, 0, vmax_right)

        base_size = sinfo.get('size', 0.050)
        r = base_size * (0.9 + 0.2 * norm_val)
        
        circle = plt.Circle((sinfo['x'], sinfo['y']), r,
                              color=col, alpha=0.92,
                              ec='white', linewidth=2.0, zorder=5)
        ax_right.add_patch(circle)

        ax_right.text(sinfo['x'], sinfo['y'], sinfo['abbr'],
                     ha='center', va='center', fontsize=10,
                     fontweight='bold', color='white', zorder=6,
                     bbox=dict(boxstyle='round,pad=0.2', facecolor='#000000', alpha=0.6))
        
        ax_right.text(sinfo['x'], sinfo['y'] - r - 0.030, f"{int(val)}",
                     ha='center', va='top', fontsize=8,
                     color='#ffffff', fontweight='bold', zorder=6)

    # Add centered title - calculate the center between the two foot maps
    bbox_left = ax_left.get_position()
    bbox_right = ax_right.get_position()
    center_x = (bbox_left.x0 + bbox_right.x1) / 2
    
    fig.text(center_x, 0.97,
             "BILATERAL FOOT PRESSURE ANALYSIS · Frame 1/2",
             fontsize=17, fontweight='bold', color='white',
         ha='center', va='center', transform=fig.transFigure)

    # Colorbars for both feet
    cbar_ax_left = fig.add_axes([0.39, 0.05, 0.01, 0.3])
    cbar_left = plt.colorbar(im_left, cax=cbar_ax_left, orientation='vertical')
    cbar_left.set_label('Pressure (ADC)', color='white', fontsize=8)
    cbar_left.ax.yaxis.set_tick_params(color='white', labelcolor='white')
    
    cbar_ax_right = fig.add_axes([0.44,0.05, 0.01, 0.3])
    cbar_right = plt.colorbar(im_right, cax=cbar_ax_right, orientation='vertical')
    cbar_right.set_label('Pressure (ADC)', color='white', fontsize=8)
    cbar_right.ax.yaxis.set_tick_params(color='white', labelcolor='white')
    
    plt.show()

    #Panel 3: Weight Distribution (Right)
    #Figure layout
    fig = plt.figure(figsize=(24, 13), facecolor='#0d1117')
    gs = GridSpec(3, 5, figure=fig,
                  left=0.02, right=0.98, top=0.92, bottom=0.05,
                  wspace=0.3, hspace=0.40,
                  width_ratios=[1.2, 1.2, 1, 1, 1])

    fig.suptitle(
        "BILATERAL FOOT PRESSURE ANALYSIS  ·  Frame 2/2",
        fontsize=17, fontweight='bold', color='white', y=0.97
    )
    
    ax_donut_r = fig.add_subplot(gs[0, 1])
    ax_donut_r.set_facecolor('#0d1117')

    zones_ordered = ["Big Toe", "Toes", "Metatarsal", "Midfoot", "Heel"]
    pcts_r = [right_res['zone_pct'][z] for z in zones_ordered]
    colors_donut = [ZONE_COLORS[z] for z in zones_ordered]

    wedges, texts, autotexts = ax_donut_r.pie(
        pcts_r, labels=None, colors=colors_donut,
        autopct='%1.1f%%', startangle=90,
        wedgeprops=dict(width=0.5, edgecolor='#0d1117', linewidth=2),
        pctdistance=0.75,
        textprops=dict(color='white', fontsize=8)
    )
    ax_donut_r.set_title("RIGHT WEIGHT\nDISTRIBUTION", color='white',
                          fontsize=10, fontweight='bold')

    #Panel 4: Weight Distribution (Left)
    ax_donut_l = fig.add_subplot(gs[0, 2])
    ax_donut_l.set_facecolor('#0d1117')

    pcts_l = [left_res['zone_pct'][z] for z in zones_ordered]

    wedges, texts, autotexts = ax_donut_l.pie(
        pcts_l, labels=None, colors=colors_donut,
        autopct='%1.1f%%', startangle=90,
        wedgeprops=dict(width=0.5, edgecolor='#0d1117', linewidth=2),
        pctdistance=0.75,
        textprops=dict(color='white', fontsize=8)
    )
    ax_donut_l.set_title("LEFT WEIGHT\nDISTRIBUTION", color='white',
                          fontsize=10, fontweight='bold')

    #Panel 5: Medial-Lateral Balance Comparison
    ax_ml = fig.add_subplot(gs[0, 3])
    ax_ml.set_facecolor('#161b25')

    medial_pct_r = right_res['medial'] / (right_res['medial'] + right_res['lateral'] + 1e-6) * 100
    lateral_pct_r = 100 - medial_pct_r
    medial_pct_l = left_res['medial'] / (left_res['medial'] + left_res['lateral'] + 1e-6) * 100
    lateral_pct_l = 100 - medial_pct_l

    x = np.arange(2)
    width = 0.35
    
    bars_r = ax_ml.bar(x - width/2, [medial_pct_r, lateral_pct_r], width, 
                        label='Right Foot', color=['#4488FF', '#FF6644'], alpha=0.8)
    bars_l = ax_ml.bar(x + width/2, [medial_pct_l, lateral_pct_l], width,
                        label='Left Foot', color=['#44BBFF', '#FF8844'], alpha=0.8)
    
    ax_ml.set_ylabel('Percentage (%)', color='white', fontsize=9)
    ax_ml.set_title('MEDIAL / LATERAL\nBALANCE COMPARISON', color='white',
                     fontsize=10, fontweight='bold')
    ax_ml.set_xticks(x)
    ax_ml.set_xticklabels(['Medial', 'Lateral'], color='white')
    ax_ml.tick_params(colors='white')
    ax_ml.set_facecolor('#161b25')
    ax_ml.axhline(50, color='white', linewidth=1, linestyle='--', alpha=0.5)
    ax_ml.legend(fontsize=8, facecolor='#1a1f2e', edgecolor='gray', 
                  labelcolor='white', loc='upper right')
    
    for spine in ax_ml.spines.values():
        spine.set_edgecolor('#333')

    #Panel 6: Arch Evaluation Comparison
    ax_arch = fig.add_subplot(gs[1, 1:3])
    ax_arch.set_facecolor('#161b25')

    arch_names = ['Med Arch 1', 'Med Arch 2', 'Lat Arch 1', 'Lat Arch 2']
    arch_vals_r = [right_frame[9], right_frame[10], right_frame[11], right_frame[12]]
    arch_vals_l = [left_frame[9], left_frame[10], left_frame[11], left_frame[12]]
    
    x = np.arange(len(arch_names))
    width = 0.35
    
    bars_r = ax_arch.bar(x - width/2, arch_vals_r, width, label='Right Foot',
                          color='#4488FF', edgecolor='white', linewidth=0.5)
    bars_l = ax_arch.bar(x + width/2, arch_vals_l, width, label='Left Foot',
                          color='#44BB44', edgecolor='white', linewidth=0.5)
    
    ax_arch.set_xlabel('Arch Points', color='white', fontsize=9)
    ax_arch.set_ylabel('Pressure', color='white', fontsize=9)
    ax_arch.set_title('ARCH PRESSURE COMPARISON', color='white',
                       fontsize=10, fontweight='bold')
    ax_arch.set_xticks(x)
    ax_arch.set_xticklabels(arch_names, color='white', rotation=45)
    ax_arch.tick_params(colors='white')
    ax_arch.set_facecolor('#161b25')
    ax_arch.legend(fontsize=8, facecolor='#1a1f2e', edgecolor='gray',
                    labelcolor='white', loc='upper right')
    ax_arch.axhline(80, color='#44BB44', linewidth=1, linestyle='--', alpha=0.5)
    ax_arch.axhline(150, color='#FFD700', linewidth=1, linestyle='--', alpha=0.5)
    
    for spine in ax_arch.spines.values():
        spine.set_edgecolor('#333')

    #Panel 7: Metatarsal Profile Comparison
    ax_met = fig.add_subplot(gs[1, 3])
    ax_met.set_facecolor('#161b25')

    met_names = ['M1', 'M2', 'M3', 'M4']
    met_vals_r = [right_frame[5], right_frame[6], right_frame[7], right_frame[8]]
    met_vals_l = [left_frame[5], left_frame[6], left_frame[7], left_frame[8]]
    
    x = np.arange(len(met_names))
    width = 0.35
    
    bars_r = ax_met.bar(x - width/2, met_vals_r, width, label='Right',
                         color='#FF8800', edgecolor='white', linewidth=0.5)
    bars_l = ax_met.bar(x + width/2, met_vals_l, width, label='Left',
                         color='#44BB44', edgecolor='white', linewidth=0.5)
    
    ax_met.set_ylabel('Pressure', color='white', fontsize=9)
    ax_met.set_title('METATARSAL\nPROFILE', color='white',
                      fontsize=10, fontweight='bold')
    ax_met.set_xticks(x)
    ax_met.set_xticklabels(met_names, color='white')
    ax_met.tick_params(colors='white')
    ax_met.set_facecolor('#161b25')
    ax_met.axhline(600, color='#FF4444', linewidth=1, linestyle='--', alpha=0.6)
    ax_met.legend(fontsize=7, facecolor='#1a1f2e', edgecolor='gray',
                   labelcolor='white', loc='upper right')
    
    for spine in ax_met.spines.values():
        spine.set_edgecolor('#333')

    #Panel 8: Diabetic Screening Comparison
    ax_diab = fig.add_subplot(gs[2, 1:3])
    ax_diab.set_facecolor('#161b25')
    ax_diab.axis('off')
    ax_diab.set_title("DIABETIC RISK COMPARISON", color='white',
                       fontsize=10, fontweight='bold')

    risk_colors = {'Low Risk': '#44BB44', 'Moderate Risk': '#FFD700', 'High Risk': '#FF3333'}
    
    # Right foot
    rc_r = risk_colors[right_res['diabetic_risk']]
    ax_diab.add_patch(FancyBboxPatch((0.05, 0.60), 0.4, 0.25,
                                      boxstyle='round,pad=0.02',
                                      facecolor=rc_r, alpha=0.25,
                                      edgecolor=rc_r, linewidth=2))
    ax_diab.text(0.25, 0.72, "RIGHT", ha='center', va='center',
                 color='white', fontsize=10, fontweight='bold')
    ax_diab.text(0.25, 0.65, right_res['diabetic_risk'], ha='center', va='center',
                 color=rc_r, fontsize=12, fontweight='bold')
    ax_diab.text(0.25, 0.58, f"Score: {right_res['diabetic_risk_score']}/7",
                 ha='center', va='center', color='white', fontsize=8)

    # Left foot
    rc_l = risk_colors[left_res['diabetic_risk']]
    ax_diab.add_patch(FancyBboxPatch((0.55, 0.60), 0.4, 0.25,
                                      boxstyle='round,pad=0.02',
                                      facecolor=rc_l, alpha=0.25,
                                      edgecolor=rc_l, linewidth=2))
    ax_diab.text(0.75, 0.72, "LEFT", ha='center', va='center',
                 color='white', fontsize=10, fontweight='bold')
    ax_diab.text(0.75, 0.65, left_res['diabetic_risk'], ha='center', va='center',
                 color=rc_l, fontsize=12, fontweight='bold')
    ax_diab.text(0.75, 0.58, f"Score: {left_res['diabetic_risk_score']}/7",
                 ha='center', va='center', color='white', fontsize=8)

    # Primary ulcer sites
    ax_diab.text(0.5, 0.40, "Primary diabetic ulcer sites:", 
                 ha='center', color='#cccccc', fontsize=9)
    ax_diab.text(0.25, 0.30, f"Hallux: {int(right_frame[0])}",
                 ha='center', color='#cccccc', fontsize=8)
    ax_diab.text(0.75, 0.30, f"Hallux: {int(left_frame[0])}",
                 ha='center', color='#cccccc', fontsize=8)
    ax_diab.text(0.25, 0.20, f"Met 1: {int(right_frame[5])}",
                 ha='center', color='#cccccc', fontsize=8)
    ax_diab.text(0.75, 0.20, f"Met 1: {int(left_frame[5])}",
                 ha='center', color='#cccccc', fontsize=8)

    #Panel 9: Clinical Summary
    ax_sum = fig.add_subplot(gs[2, 3])
    ax_sum.set_facecolor('#161b25')
    ax_sum.axis('off')
    ax_sum.set_title("CLINICAL\nSUMMARY", color='white',
                      fontsize=10, fontweight='bold')

    summary_lines = [
        ("Peak Pressure R/L",  f"{int(right_res['max_pressure'])} / {int(left_res['max_pressure'])}"),
        ("Mean Pressure R/L",  f"{right_res['mean_pressure']:.1f} / {left_res['mean_pressure']:.1f}"),
        ("Arch Status R",      right_res['flat_foot']),
        ("Arch Status L",      left_res['flat_foot']),
        ("M/L Ratio R/L",      f"{right_res['ml_ratio']:.2f} / {left_res['ml_ratio']:.2f}"),
        ("F/H Ratio R/L",      f"{right_res['fh_ratio']:.2f} / {left_res['fh_ratio']:.2f}"),
    ]
    for i, (label, val) in enumerate(summary_lines):
        ax_sum.text(0.05, 0.90 - i * 0.13, f"{label}:", color='#aaaaaa',
                    fontsize=8, transform=ax_sum.transAxes)
        ax_sum.text(0.98, 0.90 - i * 0.13, val, color='white',
                    fontsize=8, fontweight='bold', ha='right',
                    transform=ax_sum.transAxes)

    if save:
        plt.savefig(f'bilateral_foot_heatmap_frame_{frame_idx}.png',
                    dpi=150, bbox_inches='tight', facecolor='#0d1117')
        print(f"Saved: bilateral_foot_heatmap_frame_{frame_idx}.png")

    plt.show()
    return right_res, left_res

# TREND PLOT - Now shows both feet
def plot_trends(data):
    all_right_res = []
    all_left_res = []
    for f in data:
        r, l = analyze_feet(f)
        all_right_res.append(r)
        all_left_res.append(l)
    
    frames = np.arange(len(data))

    fig, axes = plt.subplots(4, 1, figsize=(16, 14), facecolor='#0d1117', sharex=True)
    fig.suptitle("BILATERAL FOOT PRESSURE TRENDS — All Frames",
                  color='white', fontsize=14, fontweight='bold')

    # Zone averages comparison
    ax = axes[0]
    ax.set_facecolor('#161b25')
    for zone in ["Big Toe", "Toes", "Metatarsal", "Midfoot", "Heel"]:
        vals_r = [r['zone_avg'][zone] for r in all_right_res]
        vals_l = [l['zone_avg'][zone] for l in all_left_res]
        ax.plot(frames, vals_r, '--', label=f'{zone} R', color=ZONE_COLORS[zone], linewidth=1.5)
        ax.plot(frames, vals_l, '-', label=f'{zone} L', color=ZONE_COLORS[zone], linewidth=1.5, alpha=0.7)
    ax.set_ylabel('Avg Pressure', color='white', fontsize=9)
    ax.set_title('Zone Pressure Averages (Solid=Left, Dashed=Right)', color='white', fontsize=10)
    ax.legend(fontsize=7, ncol=2, facecolor='#1a1f2e', labelcolor='white',
               edgecolor='gray', loc='upper right')
    ax.tick_params(colors='white')
    for s in ax.spines.values(): s.set_edgecolor('#333')

    # Arch pressure comparison
    ax = axes[1]
    ax.set_facecolor('#161b25')
    arch_r = [r['zone_avg']['Midfoot'] for r in all_right_res]
    arch_l = [l['zone_avg']['Midfoot'] for l in all_left_res]
    ax.plot(frames, arch_r, color='#FF8800', linewidth=2, label='Right Arch')
    ax.plot(frames, arch_l, color='#44BB44', linewidth=2, label='Left Arch')
    ax.fill_between(frames, arch_r, arch_l, alpha=0.3, color='#888888')
    ax.axhline(80, color='#FFD700', linewidth=1, linestyle='--', label='Mild threshold')
    ax.axhline(150, color='#FF8800', linewidth=1, linestyle='--', label='Moderate threshold')
    ax.axhline(250, color='#FF3333', linewidth=1, linestyle='--', label='Severe threshold')
    ax.set_ylabel('Arch Pressure', color='white', fontsize=9)
    ax.set_title('Arch Load Comparison - Flat Foot Indicator', color='white', fontsize=10)
    ax.legend(fontsize=8, facecolor='#1a1f2e', labelcolor='white',
               edgecolor='gray', loc='upper right')
    ax.tick_params(colors='white')
    for s in ax.spines.values(): s.set_edgecolor('#333')

    # M/L Ratio comparison
    ax = axes[2]
    ax.set_facecolor('#161b25')
    ml_r = [r['ml_ratio'] for r in all_right_res]
    ml_l = [l['ml_ratio'] for l in all_left_res]
    ax.plot(frames, ml_r, color='#4488FF', linewidth=2, label='Right M/L')
    ax.plot(frames, ml_l, color='#44BBFF', linewidth=2, label='Left M/L')
    ax.axhline(1.0, color='white', linewidth=1, linestyle='--', alpha=0.5, label='Balanced')
    ax.axhline(1.4, color='#FF4444', linewidth=1, linestyle='--', alpha=0.7, label='Pronation limit')
    ax.axhline(0.7, color='#4488FF', linewidth=1, linestyle='--', alpha=0.7, label='Supination limit')
    ax.set_ylabel('M/L Ratio', color='white', fontsize=9)
    ax.set_title('Medial-Lateral Balance Ratio Comparison', color='white', fontsize=10)
    ax.legend(fontsize=8, facecolor='#1a1f2e', labelcolor='white',
               edgecolor='gray', loc='upper right')
    ax.tick_params(colors='white')
    for s in ax.spines.values(): s.set_edgecolor('#333')

    # Asymmetry index
    ax = axes[3]
    ax.set_facecolor('#161b25')
    asymmetry = [abs(r['ml_ratio'] - l['ml_ratio']) for r, l in zip(all_right_res, all_left_res)]
    ax.fill_between(frames, 0, asymmetry, color='#FFD700', alpha=0.5)
    ax.plot(frames, asymmetry, color='#FF8800', linewidth=2)
    ax.axhline(0.3, color='#FF4444', linewidth=1, linestyle='--', alpha=0.7, label='Significant asymmetry')
    ax.set_ylabel('Asymmetry', color='white', fontsize=9)
    ax.set_xlabel('Frame', color='white', fontsize=9)
    ax.set_title('Right-Left Asymmetry Index', color='white', fontsize=10)
    ax.legend(fontsize=8, facecolor='#1a1f2e', labelcolor='white',
               edgecolor='gray', loc='upper right')
    ax.tick_params(colors='white')
    for s in ax.spines.values(): s.set_edgecolor('#333')

    plt.tight_layout()
    plt.savefig('bilateral_foot_trends.png', dpi=150, bbox_inches='tight', facecolor='#0d1117')
    print("Saved: bilateral_foot_trends.png")
    plt.show()

# CLI REPORT

def print_report(right_res, left_res, frame_idx):
    lines = [
        "=" * 75,
        f"  BILATERAL FOOT PRESSURE CLINICAL REPORT  —  Frame {frame_idx}",
        "=" * 75,
        f"  {'':<20} {'RIGHT FOOT':^25} {'LEFT FOOT':^25}",
        "-" * 75,
        f"  Peak Pressure    : {int(right_res['max_pressure']):>10}         {int(left_res['max_pressure']):>10}",
        f"  Mean Pressure    : {right_res['mean_pressure']:>10.1f}         {left_res['mean_pressure']:>10.1f}",
        f"  Total Load       : {int(right_res['total_load']):>10}         {int(left_res['total_load']):>10}",
        "-" * 75,
        "  WEIGHT DISTRIBUTION:",
    ]
    for zone in ["Big Toe", "Toes", "Metatarsal", "Midfoot", "Heel"]:
        lines.append(f"    {zone:<18} {right_res['zone_pct'][zone]:>6.1f}% {right_res['zone_avg'][zone]:>6.1f} avg        {left_res['zone_pct'][zone]:>6.1f}% {left_res['zone_avg'][zone]:>6.1f} avg")
    
    lines += [
        "-" * 75,
        f"  ARCH EVALUATION : {right_res['flat_foot']:<18} ({right_res['arch_load_pct']:.1f}%)        {left_res['flat_foot']:<18} ({left_res['arch_load_pct']:.1f}%)",
        f"  DIABETIC RISK   : {right_res['diabetic_risk']:<12} (Score: {right_res['diabetic_risk_score']}/7)        {left_res['diabetic_risk']:<12} (Score: {left_res['diabetic_risk_score']}/7)",
    ]
    
    if right_res['diabetic_flags'] or left_res['diabetic_flags']:
        lines.append("  Risk Flags:")
        for f in right_res['diabetic_flags'][:2]:
            lines.append(f"    RIGHT:  {f}")
        for f in left_res['diabetic_flags'][:2]:
            lines.append(f"    LEFT :  {f}")
    
    lines += [
        "-" * 75,
        "  GAIT / IMBALANCE:",
        f"    Medial/Lateral ratio : {right_res['ml_ratio']:.2f}                      {left_res['ml_ratio']:.2f}",
        f"    Forefoot/Heel ratio  : {right_res['fh_ratio']:.2f}                      {left_res['fh_ratio']:.2f}",
        f"    Asymmetry Index      : {abs(right_res['ml_ratio'] - left_res['ml_ratio']):.2f}",
    ]
    
    if right_res['imbalance_flags'] or left_res['imbalance_flags']:
        lines.append("  Imbalance Flags:")
        for f in right_res['imbalance_flags']:
            lines.append(f"    RIGHT:  {f}")
        for f in left_res['imbalance_flags']:
            lines.append(f"    LEFT :  {f}")
    else:
        lines.append("    No significant imbalance detected in either foot")
    
    lines.append("=" * 75)
    print('\n'.join(lines))

# MAIN ENTRY (OFFLINE + REALTIME MODES)
if __name__ == "__main__":

    print(f"\n{'='*60}")
    print("  BILATERAL LARGE VELOSTAT FOOT PRESSURE SYSTEM")
    print(f"{'='*60}")
    print("Select mode:")
    print("  1 → Offline (file / sample data)")
    print("  2 → Real-time (Proteus COM21)")
    print(f"{'='*60}")

    mode = input("Enter mode (1 or 2): ").strip()

    # MODE 1 — OFFLINE (YOUR ORIGINAL CODE, UNCHANGED)
    if mode == "1":

        try:
            data = load_data("foot_data.txt")
        except (FileNotFoundError, ValueError) as e:
            print(f"Note: {e}\nUsing generated sample data.")
            data = generate_sample_data(80)

        print(f"\nTotal sensors   : 32 (16 per foot)")
        print(f"Frames          : {len(data)}")
        print(f"Pressure range  : {int(np.min(data))} – {int(np.max(data))}\n")

        right_res, left_res = plot_heatmap(frame_idx=-1, data=data, save=True)
        print_report(right_res, left_res, len(data) - 1)

        plot_trends(data)

        all_pairs = [analyze_feet(f) for f in data]
        all_right = [p[0] for p in all_pairs]
        all_left = [p[1] for p in all_pairs]

        print("\nSESSION SUMMARY")
        print(f"Avg arch pressure (R/L): "
              f"{np.mean([r['zone_avg']['Midfoot'] for r in all_right]):.1f} / "
              f"{np.mean([l['zone_avg']['Midfoot'] for l in all_left]):.1f}")

        print(f"Flat foot (mod+) R : "
              f"{sum(1 for r in all_right if r['flat_foot_risk'] >= 2)}/{len(data)}")

        print(f"Flat foot (mod+) L : "
              f"{sum(1 for l in all_left if l['flat_foot_risk'] >= 2)}/{len(data)}")

        print(f"High Diabetic Risk : "
              f"{sum(1 for r in all_right if r['diabetic_risk'] == 'High Risk')}/{len(data)} (R)  "
              f"{sum(1 for l in all_left if l['diabetic_risk'] == 'High Risk')}/{len(data)} (L)")

    # MODE 2 — REAL-TIME (COM21 PROTEUS)
    elif mode == "2":

        COM_PORT = "COM21"
        BAUD_RATE = 9600
        try:
            ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
            time.sleep(2)
            print(f"\nConnected to {COM_PORT}")
        except Exception as e:
            print(f"Serial error: {e}")
            exit()
        plt.ion()
        try:
            while True:
                while True:
                    line = ser.readline().decode().strip()                
                    if line:
                        print("RAW:", line)   # ← ADD THIS DEBUG LINE               
                    try:
                        values = list(map(float, line.split(",")))                
                        print("Length:", len(values))  # ← ADD THIS                
                        if len(values) == 32:
                            print("VALID FRAME RECEIVED")  # ← ADD THIS                
                            data = np.array([values])              
                            plt.clf()
                            right_res, left_res = plot_heatmap(
                                frame_idx=0,
                                data=data,
                                save=False
                            )                
                            plt.pause(0.001)                
                    except:
                        pass
        except KeyboardInterrupt:
            print("\nStopping real-time mode.")
        finally:
            ser.close()
    else:
        print("Invalid mode selected.")
