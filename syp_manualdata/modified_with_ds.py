# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 10:40:27 2026

@author: Ghufran
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch, Circle, Polygon, FancyArrowPatch
from matplotlib.colors import LinearSegmentedColormap
from scipy.ndimage import gaussian_filter

import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# 16-SENSOR ANATOMICAL LAYOUT
#
# Physical layout on insole (top = toes, bottom = heel):
#
#   Col:     0          1
#   Row 0: [BT_med]  [BT_lat]      ← Big Toe (2 sensors)
#   Row 1: [Toe2]    [Toe3]        ← Toes row A
#   Row 2: [Toe4]    [Toe5]        ← Toes row B
#   Row 3: [Met1]    [Met2]        ← Metatarsals A
#   Row 4: [Met3]    [Met4]        ← Metatarsals B
#   Row 5: [Met5]    [---]         ← Metatarsal 5 (lateral, single)
#   Row 6: [Arch_M]  [Arch_C]      ← Midfoot/Arch A
#   Row 7: [Arch_L]  [---]         ← Arch lateral (single)
#   Row 8: [Heel_M]  [Heel_L]      ← Heel (2 sensors)
#
# CSV row format (16 values, sensor index 0-15):
#   0:BT_med, 1:BT_lat, 2:Toe2, 3:Toe3, 4:Toe4, 5:Toe5,
#   6:Met1, 7:Met2, 8:Met3, 9:Met4, 10:Met5,
#   11:Arch_M, 12:Arch_C, 13:Arch_L,
#   14:Heel_M, 15:Heel_L
# =============================================================================

SENSORS = {
    # idx: (name, zone, x_norm, y_norm, clinical_note)
    # x/y are normalized 0-1 positions on the foot outline (x=medial→lateral, y=toe→heel)
     0: {"name": "Hallux Med",    "zone": "Big Toe",    "x": 0.30, "y": 0.94, "abbr": "BT₁"},
     1: {"name": "Hallux Lat",   "zone": "Big Toe",    "x": 0.55, "y": 0.92, "abbr": "BT₂"},
     2: {"name": "Toe 2",        "zone": "Toes",       "x": 0.55, "y": 0.85, "abbr": "T2"},
     3: {"name": "Toe 3",        "zone": "Toes",       "x": 0.65, "y": 0.82, "abbr": "T3"},
     4: {"name": "Toe 4",        "zone": "Toes",       "x": 0.72, "y": 0.78, "abbr": "T4"},
     5: {"name": "Toe 5",        "zone": "Toes",       "x": 0.78, "y": 0.74, "abbr": "T5"},
     6: {"name": "Met 1",        "zone": "Metatarsal", "x": 0.28, "y": 0.72, "abbr": "M1"},
     7: {"name": "Met 2",        "zone": "Metatarsal", "x": 0.40, "y": 0.70, "abbr": "M2"},
     8: {"name": "Met 3",        "zone": "Metatarsal", "x": 0.52, "y": 0.68, "abbr": "M3"},
     9: {"name": "Met 4",        "zone": "Metatarsal", "x": 0.63, "y": 0.65, "abbr": "M4"},
    10: {"name": "Met 5",        "zone": "Metatarsal", "x": 0.74, "y": 0.62, "abbr": "M5"},
    11: {"name": "Arch Med",     "zone": "Midfoot",    "x": 0.22, "y": 0.50, "abbr": "AM"},
    12: {"name": "Arch Cen",     "zone": "Midfoot",    "x": 0.42, "y": 0.48, "abbr": "AC"},
    13: {"name": "Arch Lat",     "zone": "Midfoot",    "x": 0.62, "y": 0.46, "abbr": "AL"},
    14: {"name": "Heel Med",     "zone": "Heel",       "x": 0.32, "y": 0.16, "abbr": "HM"},
    15: {"name": "Heel Lat",     "zone": "Heel",       "x": 0.62, "y": 0.16, "abbr": "HL"},
}

ZONE_COLORS = {
    "Big Toe":    "#FF4444",
    "Toes":       "#FF8800",
    "Metatarsal": "#FFD700",
    "Midfoot":    "#44BB44",
    "Heel":       "#4488FF",
}

# Custom pressure colormap: blue→green→yellow→orange→red
PRESSURE_CMAP = LinearSegmentedColormap.from_list(
    "pressure",
    ["#0a0a2e", "#1a3a8f", "#2196F3", "#00BCD4", "#4CAF50",
     "#FFEB3B", "#FF9800", "#F44336", "#B71C1C"]
)

# =============================================================================
# DATA LOADING
# =============================================================================

def load_data(filename="foot_data.txt"):
    data = []
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            try:
                values = list(map(float, line.split(',')))
                if len(values) == 16:
                    data.append(values)
            except:
                continue
    if not data:
        raise ValueError("No valid 16-sensor rows found in file.")
    data = np.array(data)
    print(f"✓ Loaded {len(data)} frames | shape: {data.shape}")
    return data

def generate_sample_data(n_frames=80):
    """Realistic sample data with anatomical pressure patterns."""
    np.random.seed(42)
    data = []
    for i in range(n_frames):
        phase = (i / n_frames) * 2 * np.pi
        heel_bias = 0.5 + 0.5 * np.cos(phase)        # heel dominant early
        forefoot_bias = 0.5 + 0.5 * np.sin(phase)    # forefoot dominant late

        frame = np.array([
            # Big Toe (0,1) - peaks in push-off
            int(350 + 250 * forefoot_bias + np.random.randint(-30, 30)),
            int(280 + 180 * forefoot_bias + np.random.randint(-30, 30)),
            # Toes 2-5 (2-5)
            int(240 + 160 * forefoot_bias + np.random.randint(-25, 25)),
            int(220 + 140 * forefoot_bias + np.random.randint(-25, 25)),
            int(180 + 100 * forefoot_bias + np.random.randint(-20, 20)),
            int(140 + 80  * forefoot_bias + np.random.randint(-20, 20)),
            # Metatarsals 1-5 (6-10)
            int(420 + 200 * forefoot_bias + np.random.randint(-40, 40)),
            int(380 + 180 * forefoot_bias + np.random.randint(-35, 35)),
            int(320 + 150 * forefoot_bias + np.random.randint(-30, 30)),
            int(260 + 120 * forefoot_bias + np.random.randint(-25, 25)),
            int(200 + 90  * forefoot_bias + np.random.randint(-20, 20)),
            # Arch (11-13) - normally LOW (flat foot = high)
            int(80  + 40  * np.random.random()),
            int(60  + 30  * np.random.random()),
            int(70  + 35  * np.random.random()),
            # Heel (14-15) - peaks in heel strike
            int(480 + 300 * heel_bias + np.random.randint(-50, 50)),
            int(380 + 220 * heel_bias + np.random.randint(-40, 40)),
        ], dtype=float)
        data.append(np.clip(frame, 0, 1023))
    return np.array(data)

# =============================================================================
# CLINICAL ANALYSIS
# =============================================================================

def analyze_frame(frame):
    s = frame  # shorthand

    zones = {
        "Big Toe":    s[[0, 1]],
        "Toes":       s[[2, 3, 4, 5]],
        "Metatarsal": s[[6, 7, 8, 9, 10]],
        "Midfoot":    s[[11, 12, 13]],
        "Heel":       s[[14, 15]],
    }

    zone_avg  = {z: np.mean(v)  for z, v in zones.items()}
    zone_max  = {z: np.max(v)   for z, v in zones.items()}
    zone_sum  = {z: np.sum(v)   for z, v in zones.items()}
    total_sum = np.sum(frame)

    # --- Weight distribution % ---
    zone_pct = {z: (zone_sum[z] / total_sum * 100) if total_sum > 0 else 0
                for z in zones}

    # --- Medial vs Lateral (medial = sensors 0,6,11,14; lateral = 5,10,13,15) ---
    medial  = np.mean(s[[0, 6, 11, 14]])
    lateral = np.mean(s[[5, 10, 13, 15]])
    ml_ratio = medial / (lateral + 1e-6)

    # --- Forefoot vs Heel ---
    forefoot = np.mean(s[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]])
    heel     = np.mean(s[[14, 15]])
    fh_ratio = forefoot / (heel + 1e-6)

    # --- FLAT FOOT DETECTION ---
    # Arch sensors should be near zero in a healthy foot
    arch_avg = zone_avg["Midfoot"]
    heel_avg = zone_avg["Heel"]
    arch_load_pct = zone_pct["Midfoot"]

    if arch_avg < 100:
        flat_foot = "Normal Arch"
        flat_foot_risk = 0
    elif arch_avg < 200:
        flat_foot = "Mild Flat Foot"
        flat_foot_risk = 1
    elif arch_avg < 350:
        flat_foot = "Moderate Flat Foot"
        flat_foot_risk = 2
    else:
        flat_foot = "Severe Flat Foot"
        flat_foot_risk = 3

    # --- DIABETIC FOOT SCREENING ---
    # High-risk zones: Met1 (idx 6), Hallux medial (idx 0)
    diabetic_risk_score = 0
    diabetic_flags = []
    if s[0] > 600:
        diabetic_flags.append("Hallux Med > 600")
        diabetic_risk_score += 2
    if s[6] > 600:
        diabetic_flags.append("Met 1 > 600")
        diabetic_risk_score += 2
    if s[7] > 550:
        diabetic_flags.append("Met 2 > 550")
        diabetic_risk_score += 1
    if np.max(s[[6,7,8,9,10]]) > 700:
        diabetic_flags.append("Peak Metatarsal > 700")
        diabetic_risk_score += 2

    if diabetic_risk_score == 0:
        diabetic_risk = "Low Risk"
    elif diabetic_risk_score <= 2:
        diabetic_risk = "Moderate Risk"
    else:
        diabetic_risk = "High Risk"

    # --- WEIGHT IMBALANCE ---
    imbalance_flags = []
    if ml_ratio > 1.4:
        imbalance_flags.append("Medial overload (Pronation)")
    elif ml_ratio < 0.7:
        imbalance_flags.append("Lateral overload (Supination)")

    if fh_ratio > 1.6:
        imbalance_flags.append("Forefoot dominant gait")
    elif fh_ratio < 0.5:
        imbalance_flags.append("Heel dominant gait")

    # Metatarsal load balance
    met_pressures = s[[6, 7, 8, 9, 10]]
    if np.std(met_pressures) > 120:
        imbalance_flags.append("Uneven metatarsal loading")

    return {
        "zones": zones,
        "zone_avg": zone_avg,
        "zone_max": zone_max,
        "zone_pct": zone_pct,
        "medial": medial,
        "lateral": lateral,
        "ml_ratio": ml_ratio,
        "forefoot": forefoot,
        "heel": heel,
        "fh_ratio": fh_ratio,
        "flat_foot": flat_foot,
        "flat_foot_risk": flat_foot_risk,
        "arch_load_pct": arch_load_pct,
        "diabetic_risk": diabetic_risk,
        "diabetic_risk_score": diabetic_risk_score,
        "diabetic_flags": diabetic_flags,
        "imbalance_flags": imbalance_flags,
        "max_pressure": np.max(frame),
        "mean_pressure": np.mean(frame),
        "total_load": np.sum(frame),
    }

# =============================================================================
# IMPROVED FOOT OUTLINE SHAPE - More anatomically accurate
# =============================================================================

def draw_foot_outline(ax, alpha=0.15):
    """Draw anatomically-shaped right foot outline with improved realism."""
    
    # Create more detailed foot outline points
    # Starting from medial heel, going around to lateral heel
    
    # Main foot outline - right foot, normalized coordinates (0-1)
    # More anatomical shape with distinct arch, heel, and toe contours
    
    # Medial side (inner arch) - more pronounced curve
    medial_x = [0.38, 0.35, 0.32, 0.28, 0.24, 0.22, 0.20, 0.19, 0.18, 0.18, 
                0.19, 0.21, 0.23, 0.26, 0.29, 0.32, 0.35, 0.38]
    medial_y = [0.04, 0.08, 0.12, 0.16, 0.22, 0.28, 0.35, 0.42, 0.50, 0.58,
                0.65, 0.72, 0.78, 0.83, 0.88, 0.92, 0.95, 0.98]
    
    # Toe area - five distinct toe bumps
    toe_x = [0.38, 0.42, 0.47, 0.52, 0.57, 0.62, 0.67, 0.72, 0.77, 0.80]
    toe_y = [0.98, 0.99, 0.99, 0.98, 0.97, 0.95, 0.92, 0.88, 0.83, 0.78]
    
    # Lateral side (outside) - straighter
    lateral_x = [0.80, 0.79, 0.78, 0.76, 0.74, 0.72, 0.70, 0.68, 0.66, 0.64,
                 0.62, 0.60, 0.58, 0.56, 0.54, 0.52, 0.50]
    lateral_y = [0.78, 0.72, 0.66, 0.60, 0.54, 0.48, 0.42, 0.36, 0.30, 0.24,
                 0.19, 0.15, 0.11, 0.08, 0.06, 0.04, 0.04]
    
    # Heel area - rounded
    heel_x = [0.50, 0.47, 0.44, 0.41, 0.38]
    heel_y = [0.04, 0.03, 0.02, 0.02, 0.04]
    
    # Combine all points to create closed outline
    outline_x = medial_x + toe_x + lateral_x + heel_x
    outline_y = medial_y + toe_y + lateral_y + heel_y
    
    # Fill the foot with skin tone
    ax.fill(outline_x, outline_y, color='#e8d5b7', alpha=alpha, zorder=0)
    
    # Draw outline with darker border
    ax.plot(outline_x, outline_y, color='#8B7355', linewidth=2, alpha=0.6, zorder=1)
    
    # Add anatomical details
    
    # Toe separators (subtle lines between toes)
    toe_sep_x = [0.42, 0.47, 0.52, 0.57, 0.62, 0.67]
    toe_sep_y_start = [0.97, 0.96, 0.94, 0.91, 0.87, 0.82]
    toe_sep_y_end = [0.92, 0.91, 0.89, 0.86, 0.82, 0.77]
    
    for i in range(len(toe_sep_x)):
        ax.plot([toe_sep_x[i]-0.01, toe_sep_x[i]+0.01], 
                [toe_sep_y_start[i], toe_sep_y_end[i]], 
                color='#8B7355', linewidth=0.8, alpha=0.4, zorder=1)
    
    # Arch line (medial longitudinal arch)
    arch_x = [0.20, 0.22, 0.24, 0.26, 0.28]
    arch_y = [0.45, 0.52, 0.58, 0.64, 0.69]
    ax.plot(arch_x, arch_y, color='#8B7355', linewidth=1, alpha=0.3, 
            linestyle='--', zorder=1)
    
    # Heel contour
    heel_center_x, heel_center_y = 0.44, 0.08
    heel_circle = plt.Circle((heel_center_x, heel_center_y), 0.06, 
                              color='#8B7355', alpha=0.1, linewidth=1,
                              fill=False, linestyle=':', zorder=1)
    ax.add_patch(heel_circle)
    
    # Metatarsal heads line (ball of foot)
    met_x = [0.28, 0.40, 0.52, 0.63, 0.74]
    met_y = [0.72, 0.70, 0.68, 0.65, 0.62]
    ax.plot(met_x, met_y, color='#8B7355', linewidth=1.2, alpha=0.4, zorder=1)
    
    # Add subtle shading for 3D effect
    # Heel pad
    heel_pad = plt.Circle((0.44, 0.08), 0.08, color='#c9b396', alpha=0.2, zorder=0)
    ax.add_patch(heel_pad)
    
    # Ball of foot
    ball_pad = plt.Circle((0.50, 0.70), 0.12, color='#c9b396', alpha=0.15, zorder=0)
    ax.add_patch(ball_pad)

def pressure_to_color(value, vmin=0, vmax=1023):
    norm = np.clip((value - vmin) / (vmax - vmin), 0, 1)
    return PRESSURE_CMAP(norm)

# =============================================================================
# MAIN HEATMAP VISUALIZATION
# =============================================================================

def plot_heatmap(frame_idx=-1, data=None, save=True):
    if data is None:
        raise ValueError("Pass data array.")
    if frame_idx == -1:
        frame_idx = len(data) - 1
    frame = data[frame_idx]
    res = analyze_frame(frame)

    # ── Figure layout ─────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(20, 13), facecolor='#0d1117')
    gs = GridSpec(3, 4, figure=fig,
                  left=0.04, right=0.96, top=0.92, bottom=0.05,
                  wspace=0.35, hspace=0.40,
                  width_ratios=[1.6, 1, 1, 1])

    title = fig.suptitle(
        f"FOOT PRESSURE ANALYSIS  ·  Frame {frame_idx + 1}/{len(data)}",
        fontsize=17, fontweight='bold', color='white', y=0.97
    )

    # ── Panel 1: Anatomical Foot Heatmap ──────────────────────────────────────
    ax_foot = fig.add_subplot(gs[:, 0])
    ax_foot.set_facecolor('#0d1117')
    ax_foot.set_xlim(0, 1)
    ax_foot.set_ylim(0, 1)
    ax_foot.set_aspect('equal')
    ax_foot.axis('off')
    ax_foot.set_title("PRESSURE MAP", color='white', fontsize=13,
                       fontweight='bold', pad=12)

    draw_foot_outline(ax_foot)

    # Draw Gaussian-blended heatmap overlay using scatter
    # Build a fine grid and accumulate Gaussian blobs
    grid_size = 200
    heatmap = np.zeros((grid_size, grid_size))
    vmax = max(np.max(frame), 1)

    xs = np.linspace(0, 1, grid_size)
    ys = np.linspace(0, 1, grid_size)
    XX, YY = np.meshgrid(xs, ys)

    for idx, sinfo in SENSORS.items():
        val = frame[idx]
        sx, sy = sinfo['x'], sinfo['y']
        sigma = 0.055
        blob = np.exp(-((XX - sx)**2 + (YY - sy)**2) / (2 * sigma**2))
        heatmap += blob * val

    # Normalize
    heatmap_norm = heatmap / (np.max(heatmap) + 1e-6)
    
    # Create a more accurate foot-shaped mask using the outline
    from matplotlib.path import Path
    
    # Define foot outline path
    outline_x = [0.38, 0.35, 0.32, 0.28, 0.24, 0.22, 0.20, 0.19, 0.18, 0.18, 
                 0.19, 0.21, 0.23, 0.26, 0.29, 0.32, 0.35, 0.38,
                 0.42, 0.47, 0.52, 0.57, 0.62, 0.67, 0.72, 0.77, 0.80,
                 0.79, 0.78, 0.76, 0.74, 0.72, 0.70, 0.68, 0.66, 0.64,
                 0.62, 0.60, 0.58, 0.56, 0.54, 0.52, 0.50,
                 0.47, 0.44, 0.41, 0.38]
    outline_y = [0.04, 0.08, 0.12, 0.16, 0.22, 0.28, 0.35, 0.42, 0.50, 0.58,
                 0.65, 0.72, 0.78, 0.83, 0.88, 0.92, 0.95, 0.98,
                 0.99, 0.99, 0.98, 0.97, 0.95, 0.92, 0.88, 0.83, 0.78,
                 0.72, 0.66, 0.60, 0.54, 0.48, 0.42, 0.36, 0.30, 0.24,
                 0.19, 0.15, 0.11, 0.08, 0.06, 0.04, 0.04,
                 0.03, 0.02, 0.02, 0.04]
    
    foot_path = Path(np.column_stack([outline_x, outline_y]))
    points = np.column_stack([XX.ravel(), YY.ravel()])
    mask = ~foot_path.contains_points(points).reshape(XX.shape)
    heatmap_norm[mask] = np.nan

    im = ax_foot.imshow(
        heatmap_norm,
        origin='lower', extent=[0, 1, 0, 1],
        cmap=PRESSURE_CMAP, alpha=0.75,
        vmin=0, vmax=1, zorder=2, aspect='auto'
    )

    # Draw sensor dots + labels
    for idx, sinfo in SENSORS.items():
        val = frame[idx]
        norm_val = val / vmax
        col = pressure_to_color(val, 0, vmax)

        # Sensor circle — size proportional to pressure
        r = 0.028 + 0.022 * norm_val
        circle = plt.Circle((sinfo['x'], sinfo['y']), r,
                              color=col, alpha=0.92,
                              ec='white', linewidth=0.8, zorder=5)
        ax_foot.add_patch(circle)

        # Abbr label
        ax_foot.text(sinfo['x'], sinfo['y'] + 0.001, sinfo['abbr'],
                     ha='center', va='center', fontsize=6.5,
                     fontweight='bold', color='black', zorder=6)

        # Value label below
        ax_foot.text(sinfo['x'], sinfo['y'] - r - 0.025, f"{int(val)}",
                     ha='center', va='top', fontsize=6,
                     color='#cccccc', zorder=6)

    # Zone bracket labels on left side
    zone_y = {"Big Toe": 0.93, "Toes": 0.82, "Metatarsal": 0.67,
               "Midfoot": 0.49, "Heel": 0.16}
    for zone, zy in zone_y.items():
        ax_foot.text(-0.04, zy, zone, ha='right', va='center',
                     fontsize=8, color=ZONE_COLORS[zone],
                     fontweight='bold',
                     transform=ax_foot.transData)
        ax_foot.annotate('', xy=(0.08, zy), xytext=(-0.02, zy),
                          arrowprops=dict(arrowstyle='->', color=ZONE_COLORS[zone],
                                          lw=1.2),
                          xycoords='data', textcoords='data')

    # Colorbar
    cbar = plt.colorbar(im, ax=ax_foot, orientation='vertical',
                         fraction=0.035, pad=0.02)
    cbar.set_label('Pressure (ADC units)', color='white', fontsize=9)
    cbar.ax.yaxis.set_tick_params(color='white', labelcolor='white')
    cbar.set_ticks([0, 0.25, 0.5, 0.75, 1.0])
    cbar.set_ticklabels(['0', f'{int(vmax*0.25)}', f'{int(vmax*0.5)}',
                          f'{int(vmax*0.75)}', f'{int(vmax)}'])

    # ── Panel 2: Weight Distribution Donut ───────────────────────────────────
    ax_donut = fig.add_subplot(gs[0, 1])
    ax_donut.set_facecolor('#0d1117')

    zones_ordered = ["Big Toe", "Toes", "Metatarsal", "Midfoot", "Heel"]
    pcts = [res['zone_pct'][z] for z in zones_ordered]
    colors_donut = [ZONE_COLORS[z] for z in zones_ordered]

    wedges, texts, autotexts = ax_donut.pie(
        pcts, labels=None, colors=colors_donut,
        autopct='%1.1f%%', startangle=90,
        wedgeprops=dict(width=0.5, edgecolor='#0d1117', linewidth=2),
        pctdistance=0.75,
        textprops=dict(color='white', fontsize=8)
    )
    ax_donut.set_title("WEIGHT\nDISTRIBUTION", color='white',
                        fontsize=10, fontweight='bold')

    legend_patches = [mpatches.Patch(color=ZONE_COLORS[z], label=f"{z}: {pcts[i]:.1f}%")
                      for i, z in enumerate(zones_ordered)]
    ax_donut.legend(handles=legend_patches, loc='lower center',
                    bbox_to_anchor=(0.5, -0.35), fontsize=7.5,
                    facecolor='#1a1f2e', edgecolor='gray',
                    labelcolor='white', framealpha=0.8)

    # ── Panel 3: Medial-Lateral Balance Bar ──────────────────────────────────
    ax_ml = fig.add_subplot(gs[0, 2])
    ax_ml.set_facecolor('#161b25')

    medial_pct  = res['medial']  / (res['medial'] + res['lateral'] + 1e-6) * 100
    lateral_pct = 100 - medial_pct

    bars = ax_ml.barh(['Medial', 'Lateral'],
                       [medial_pct, lateral_pct],
                       color=['#4488FF', '#FF6644'],
                       height=0.5, edgecolor='white', linewidth=0.5)
    ax_ml.set_xlim(0, 100)
    ax_ml.axvline(50, color='white', linewidth=1, linestyle='--', alpha=0.5)
    ax_ml.set_title("MEDIAL / LATERAL\nBALANCE", color='white',
                     fontsize=10, fontweight='bold')
    ax_ml.tick_params(colors='white')
    ax_ml.set_facecolor('#161b25')
    for spine in ax_ml.spines.values():
        spine.set_edgecolor('#333')
    for bar, val in zip(bars, [medial_pct, lateral_pct]):
        ax_ml.text(val + 1, bar.get_y() + bar.get_height()/2,
                   f'{val:.1f}%', va='center', color='white', fontsize=10)

    ml_label = "Pronation Risk" if res['ml_ratio'] > 1.4 else \
               "Supination Risk" if res['ml_ratio'] < 0.7 else "Balanced"
    ax_ml.text(50, -0.6, ml_label, ha='center', color='#FFD700',
                fontsize=9, fontweight='bold', transform=ax_ml.transData)

    # ── Panel 4: Forefoot vs Heel Balance ────────────────────────────────────
    ax_fh = fig.add_subplot(gs[0, 3])
    ax_fh.set_facecolor('#161b25')

    forefoot_zones = ["Big Toe", "Toes", "Metatarsal"]
    heel_zones     = ["Midfoot", "Heel"]
    ff_pct = sum(res['zone_pct'][z] for z in forefoot_zones)
    h_pct  = sum(res['zone_pct'][z] for z in heel_zones)

    colors_fh = ['#FF8800', '#4488FF']
    ax_fh.bar(['Forefoot', 'Hindfoot'], [ff_pct, h_pct],
               color=colors_fh, edgecolor='white', linewidth=0.5)
    ax_fh.axhline(50, color='white', linewidth=1, linestyle='--', alpha=0.5)
    ax_fh.set_ylim(0, 100)
    ax_fh.set_ylabel('%', color='white', fontsize=9)
    ax_fh.set_title("FOREFOOT /\nHINDFOOT %", color='white',
                     fontsize=10, fontweight='bold')
    ax_fh.tick_params(colors='white')
    for spine in ax_fh.spines.values():
        spine.set_edgecolor('#333')
    for i, (label, val) in enumerate(zip(['Forefoot', 'Hindfoot'], [ff_pct, h_pct])):
        ax_fh.text(i, val + 1.5, f'{val:.1f}%', ha='center',
                   color='white', fontsize=10, fontweight='bold')

    # ── Panel 5: Flat Foot / Arch Evaluation ─────────────────────────────────
    ax_arch = fig.add_subplot(gs[1, 1:3])
    ax_arch.set_facecolor('#161b25')

    # Arch index visualization: bar per arch sensor
    arch_names = ["Arch Med", "Arch Cen", "Arch Lat"]
    arch_vals  = [frame[11], frame[12], frame[13]]
    arch_colors = []
    for v in arch_vals:
        if v < 100:   arch_colors.append('#44BB44')
        elif v < 200: arch_colors.append('#FFD700')
        elif v < 350: arch_colors.append('#FF8800')
        else:         arch_colors.append('#FF3333')

    bars = ax_arch.bar(arch_names, arch_vals, color=arch_colors,
                        edgecolor='white', linewidth=0.5)
    ax_arch.axhline(100, color='#44BB44', linewidth=1.2, linestyle='--',
                     alpha=0.7, label='Normal threshold')
    ax_arch.axhline(200, color='#FFD700', linewidth=1.2, linestyle='--',
                     alpha=0.7, label='Mild flat foot')
    ax_arch.axhline(350, color='#FF3333', linewidth=1.2, linestyle='--',
                     alpha=0.7, label='Moderate flat foot')
    ax_arch.set_ylim(0, max(500, max(arch_vals) * 1.2))
    ax_arch.set_title(
        f"ARCH / FLAT FOOT EVALUATION  —  {res['flat_foot']}  (Arch load: {res['arch_load_pct']:.1f}%)",
        color='white', fontsize=10, fontweight='bold'
    )
    ax_arch.tick_params(colors='white')
    ax_arch.set_facecolor('#161b25')
    for spine in ax_arch.spines.values():
        spine.set_edgecolor('#333')
    ax_arch.legend(fontsize=7.5, facecolor='#1a1f2e',
                   edgecolor='gray', labelcolor='white')
    for bar, val in zip(bars, arch_vals):
        ax_arch.text(bar.get_x() + bar.get_width()/2, val + 8,
                     f'{int(val)}', ha='center', color='white', fontsize=9)

    # Flat foot risk badge
    ff_badge_color = ['#44BB44', '#FFD700', '#FF8800', '#FF3333'][res['flat_foot_risk']]
    ax_arch.text(2.6, max(arch_vals) * 0.9, res['flat_foot'],
                 ha='center', color='black', fontsize=10, fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.4', facecolor=ff_badge_color, alpha=0.9))

    # ── Panel 6: Diabetic Screening ───────────────────────────────────────────
    ax_diab = fig.add_subplot(gs[1, 3])
    ax_diab.set_facecolor('#161b25')
    ax_diab.axis('off')
    ax_diab.set_title("DIABETIC FOOT\nSCREENING", color='white',
                       fontsize=10, fontweight='bold')

    risk_colors = {'Low Risk': '#44BB44', 'Moderate Risk': '#FFD700', 'High Risk': '#FF3333'}
    rc = risk_colors[res['diabetic_risk']]

    ax_diab.add_patch(FancyBboxPatch((0.05, 0.65), 0.9, 0.28,
                                      boxstyle='round,pad=0.02',
                                      facecolor=rc, alpha=0.25,
                                      edgecolor=rc, linewidth=2))
    ax_diab.text(0.5, 0.79, res['diabetic_risk'], ha='center', va='center',
                 color=rc, fontsize=15, fontweight='bold')
    ax_diab.text(0.5, 0.69, f"Score: {res['diabetic_risk_score']}/7",
                 ha='center', va='center', color='white', fontsize=9)

    if res['diabetic_flags']:
        ax_diab.text(0.5, 0.58, "Risk Flags:", ha='center',
                     color='#FF8800', fontsize=9, fontweight='bold')
        for i, flag in enumerate(res['diabetic_flags'][:4]):
            ax_diab.text(0.5, 0.47 - i*0.12, f"⚠ {flag}",
                         ha='center', color='#FFD700', fontsize=8)
    else:
        ax_diab.text(0.5, 0.45, "✓ No high-risk\npressure zones",
                     ha='center', color='#44BB44', fontsize=10, va='top')

    # Highlight sensors: Met1 (6) and Hallux Med (0)
    ax_diab.text(0.5, 0.12,
                 f"Hallux Med: {int(frame[0])}   Met 1: {int(frame[6])}",
                 ha='center', color='#cccccc', fontsize=8.5)
    ax_diab.text(0.5, 0.04, "(Primary diabetic ulcer sites)",
                 ha='center', color='gray', fontsize=7.5, style='italic')

    # ── Panel 7: Metatarsal Profile ───────────────────────────────────────────
    ax_met = fig.add_subplot(gs[2, 1:3])
    ax_met.set_facecolor('#161b25')

    met_vals  = [frame[6], frame[7], frame[8], frame[9], frame[10]]
    met_names = ['Met 1\n(Medial)', 'Met 2', 'Met 3', 'Met 4', 'Met 5\n(Lateral)']
    met_colors = [pressure_to_color(v, 0, vmax) for v in met_vals]

    bars = ax_met.bar(met_names, met_vals, color=met_colors,
                       edgecolor='white', linewidth=0.5)
    ax_met.set_title("METATARSAL HEAD PRESSURE PROFILE", color='white',
                      fontsize=10, fontweight='bold')
    ax_met.tick_params(colors='white')
    ax_met.set_facecolor('#161b25')
    ax_met.set_ylabel('Pressure', color='white', fontsize=9)
    for spine in ax_met.spines.values():
        spine.set_edgecolor('#333')
    for bar, val in zip(bars, met_vals):
        ax_met.text(bar.get_x() + bar.get_width()/2, val + 8,
                    f'{int(val)}', ha='center', color='white', fontsize=9)
    ax_met.axhline(600, color='#FF4444', linewidth=1, linestyle='--',
                    alpha=0.6, label='Diabetic risk threshold')
    ax_met.legend(fontsize=8, facecolor='#1a1f2e',
                  edgecolor='gray', labelcolor='white')

    # ── Panel 8: Summary / Imbalance Flags ───────────────────────────────────
    ax_sum = fig.add_subplot(gs[2, 3])
    ax_sum.set_facecolor('#161b25')
    ax_sum.axis('off')
    ax_sum.set_title("CLINICAL\nSUMMARY", color='white',
                      fontsize=10, fontweight='bold')

    summary_lines = [
        ("Peak Pressure",    f"{int(res['max_pressure'])}"),
        ("Mean Pressure",    f"{res['mean_pressure']:.1f}"),
        ("Arch Status",      res['flat_foot']),
        ("Diabetic Risk",    res['diabetic_risk']),
        ("M/L Ratio",        f"{res['ml_ratio']:.2f}"),
        ("F/H Ratio",        f"{res['fh_ratio']:.2f}"),
    ]
    for i, (label, val) in enumerate(summary_lines):
        ax_sum.text(0.05, 0.90 - i * 0.13, f"{label}:", color='#aaaaaa',
                    fontsize=8.5, transform=ax_sum.transAxes)
        ax_sum.text(0.98, 0.90 - i * 0.13, val, color='white',
                    fontsize=8.5, fontweight='bold', ha='right',
                    transform=ax_sum.transAxes)

    if res['imbalance_flags']:
        ax_sum.text(0.5, 0.08, "⚠ " + "  ⚠ ".join(res['imbalance_flags'][:2]),
                    ha='center', color='#FFD700', fontsize=7.5,
                    transform=ax_sum.transAxes, wrap=True)

    # ── Panel 9: Pressure over time (sensor trends) ───────────────────────────
    ax_trend = fig.add_subplot(gs[2, 1])
    # Reuse ax_met space cleanly — overwrite positioning
    # Actually already placed ax_met at gs[2,1:3], so let's add trend below labels
    # Skip dedicated trend panel to avoid overlap; use ax_met extended

    plt.savefig(f'foot_heatmap_frame_{frame_idx}.png',
                dpi=150, bbox_inches='tight', facecolor='#0d1117')
    print(f"✓ Saved: foot_heatmap_frame_{frame_idx}.png")
    plt.show()

    return res

# =============================================================================
# MULTI-FRAME TREND PLOT
# =============================================================================

def plot_trends(data):
    """Plot key metrics over all frames."""
    all_res = [analyze_frame(f) for f in data]
    frames  = np.arange(len(data))

    fig, axes = plt.subplots(3, 1, figsize=(16, 10), facecolor='#0d1117',
                              sharex=True)
    fig.suptitle("FOOT PRESSURE TRENDS — All Frames",
                  color='white', fontsize=14, fontweight='bold')

    # 1. Zone averages
    ax = axes[0]
    ax.set_facecolor('#161b25')
    for zone in ["Big Toe", "Toes", "Metatarsal", "Midfoot", "Heel"]:
        vals = [r['zone_avg'][zone] for r in all_res]
        ax.plot(frames, vals, label=zone, color=ZONE_COLORS[zone], linewidth=1.8)
    ax.set_ylabel('Avg Pressure', color='white', fontsize=9)
    ax.set_title('Zone Pressure Averages', color='white', fontsize=10)
    ax.legend(fontsize=8, facecolor='#1a1f2e', labelcolor='white',
               edgecolor='gray', loc='upper right')
    ax.tick_params(colors='white')
    for s in ax.spines.values(): s.set_edgecolor('#333')

    # 2. Arch (flat foot indicator)
    ax = axes[1]
    ax.set_facecolor('#161b25')
    arch_avgs = [r['zone_avg']['Midfoot'] for r in all_res]
    ax.fill_between(frames, arch_avgs, color='#44BB44', alpha=0.4)
    ax.plot(frames, arch_avgs, color='#44BB44', linewidth=2, label='Arch Pressure')
    ax.axhline(100, color='#FFD700', linewidth=1, linestyle='--', label='Mild flat foot')
    ax.axhline(200, color='#FF8800', linewidth=1, linestyle='--', label='Moderate flat foot')
    ax.axhline(350, color='#FF3333', linewidth=1, linestyle='--', label='Severe flat foot')
    ax.set_ylabel('Arch Pressure', color='white', fontsize=9)
    ax.set_title('Arch Load — Flat Foot Indicator', color='white', fontsize=10)
    ax.legend(fontsize=8, facecolor='#1a1f2e', labelcolor='white',
               edgecolor='gray', loc='upper right')
    ax.tick_params(colors='white')
    for s in ax.spines.values(): s.set_edgecolor('#333')

    # 3. M/L Balance ratio
    ax = axes[2]
    ax.set_facecolor('#161b25')
    ml_vals = [r['ml_ratio'] for r in all_res]
    ax.plot(frames, ml_vals, color='#BB88FF', linewidth=2, label='M/L Ratio')
    ax.axhline(1.0, color='white', linewidth=1, linestyle='--', alpha=0.5, label='Balanced')
    ax.axhline(1.4, color='#FF4444', linewidth=1, linestyle='--', alpha=0.7, label='Pronation limit')
    ax.axhline(0.7, color='#4488FF', linewidth=1, linestyle='--', alpha=0.7, label='Supination limit')
    ax.set_ylabel('M/L Ratio', color='white', fontsize=9)
    ax.set_xlabel('Frame', color='white', fontsize=9)
    ax.set_title('Medial-Lateral Balance Ratio', color='white', fontsize=10)
    ax.legend(fontsize=8, facecolor='#1a1f2e', labelcolor='white',
               edgecolor='gray', loc='upper right')
    ax.tick_params(colors='white')
    for s in ax.spines.values(): s.set_edgecolor('#333')

    plt.tight_layout()
    plt.savefig('foot_trends.png', dpi=150, bbox_inches='tight', facecolor='#0d1117')
    print("✓ Saved: foot_trends.png")
    plt.show()

# =============================================================================
# CLI REPORT
# =============================================================================

def print_report(res, frame_idx):
    lines = [
        "=" * 65,
        f"  FOOT PRESSURE CLINICAL REPORT  —  Frame {frame_idx}",
        "=" * 65,
        f"  Peak: {int(res['max_pressure'])}   Mean: {res['mean_pressure']:.1f}   "
        f"Total Load: {int(res['total_load'])}",
        "-" * 65,
        "  WEIGHT DISTRIBUTION:",
    ]
    for zone in ["Big Toe", "Toes", "Metatarsal", "Midfoot", "Heel"]:
        lines.append(f"    {zone:<18} avg={res['zone_avg'][zone]:.1f}   "
                     f"{res['zone_pct'][zone]:.1f}%")
    lines += [
        "-" * 65,
        f"  ARCH EVALUATION : {res['flat_foot']}  (arch load {res['arch_load_pct']:.1f}%)",
        f"  DIABETIC RISK   : {res['diabetic_risk']}",
    ]
    if res['diabetic_flags']:
        for f in res['diabetic_flags']:
            lines.append(f"    ⚠  {f}")
    lines += [
        "-" * 65,
        "  GAIT / IMBALANCE:",
        f"    Medial/Lateral ratio : {res['ml_ratio']:.2f}",
        f"    Forefoot/Heel ratio  : {res['fh_ratio']:.2f}",
    ]
    if res['imbalance_flags']:
        for f in res['imbalance_flags']:
            lines.append(f"    ⚠  {f}")
    else:
        lines.append("    ✓  No significant imbalance detected")
    lines.append("=" * 65)
    print('\n'.join(lines))

# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # ── Load data ─────────────────────────────────────────────────────────────
    try:
        data = load_data("foot_data.txt")
    except (FileNotFoundError, ValueError) as e:
        print(f"Note: {e}\nUsing generated sample data.")
        data = generate_sample_data(80)

    print(f"\nSensor count : 16")
    print(f"Frames       : {len(data)}")
    print(f"Pressure range: {int(np.min(data))} – {int(np.max(data))}")

    # ── Analyse latest frame ──────────────────────────────────────────────────
    res = plot_heatmap(frame_idx=-1, data=data, save=True)
    print_report(res, len(data) - 1)

    # ── Trends over all frames ────────────────────────────────────────────────
    plot_trends(data)

    # ── Summary stats ─────────────────────────────────────────────────────────
    all_res = [analyze_frame(f) for f in data]
    print("\nSESSION SUMMARY")
    print(f"  Avg arch pressure  : {np.mean([r['zone_avg']['Midfoot'] for r in all_res]):.1f}")
    ff_risk = sum(1 for r in all_res if r['flat_foot_risk'] >= 2)
    print(f"  Frames with flat foot (moderate+): {ff_risk}/{len(data)}")
    high_diab = sum(1 for r in all_res if r['diabetic_risk'] == 'High Risk')
    print(f"  Frames with High Diabetic Risk: {high_diab}/{len(data)}")