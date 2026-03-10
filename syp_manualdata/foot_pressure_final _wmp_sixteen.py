# -*- coding: utf-8 -*-
"""
Professional Foot Pressure Assessment System (Pedoscan-style)
Optimized for Large Velostat Sensors - 16 Points
Author: Ghufran
"""

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

# =============================================================================
# SENSOR LAYOUT (16 sensors) - LARGE SIZE for Velostat
# idx  zone         count
#  0   Big Toe          1   — Hallux (big toe)
#  1-4 Toes             4   — One sensor per toe (positions 2-5)
#  5-8 Metatarsal       4   — Met heads 1-4 (M5 is smaller, often grouped with M4)
#  9-12 Midfoot         4   — Two medial arch, two lateral arch
# 13-15 Heel            3   — Medial, lateral, and central heel
# =============================================================================

SENSORS = {
    # ── Big Toe (1 sensor) - LARGE ────────────────────────────────────────
     0: {"name": "Hallux",        "zone": "Big Toe",    "x": 0.30, "y": 0.96, "abbr": "BT", "size": 0.055},

    # ── Toes (4 sensors) - LARGE ──────────────────────────────────────────
     1: {"name": "Toe 2",         "zone": "Toes",       "x": 0.44, "y": 0.93, "abbr": "T2", "size": 0.050},
     2: {"name": "Toe 3",         "zone": "Toes",       "x": 0.55, "y": 0.90, "abbr": "T3", "size": 0.048},
     3: {"name": "Toe 4",         "zone": "Toes",       "x": 0.66, "y": 0.86, "abbr": "T4", "size": 0.046},
     4: {"name": "Toe 5",         "zone": "Toes",       "x": 0.76, "y": 0.82, "abbr": "T5", "size": 0.044},

    # ── Metatarsals (4 sensors) - LARGE ────────────────────────────────────
     5: {"name": "Met 1",         "zone": "Metatarsal", "x": 0.28, "y": 0.76, "abbr": "M1", "size": 0.060},
     6: {"name": "Met 2",         "zone": "Metatarsal", "x": 0.41, "y": 0.72, "abbr": "M2", "size": 0.058},
     7: {"name": "Met 3",         "zone": "Metatarsal", "x": 0.54, "y": 0.68, "abbr": "M3", "size": 0.056},
     8: {"name": "Met 4-5",       "zone": "Metatarsal", "x": 0.68, "y": 0.64, "abbr": "M4", "size": 0.054},

    # ── Midfoot / Arch (4 sensors) - LARGE ─────────────────────────────────
     9: {"name": "Medial Arch 1", "zone": "Midfoot",    "x": 0.24, "y": 0.52, "abbr": "MA1", "size": 0.048},
    10: {"name": "Medial Arch 2", "zone": "Midfoot",    "x": 0.27, "y": 0.42, "abbr": "MA2", "size": 0.048},
    11: {"name": "Lateral Arch 1","zone": "Midfoot",    "x": 0.56, "y": 0.48, "abbr": "LA1", "size": 0.048},
    12: {"name": "Lateral Arch 2","zone": "Midfoot",    "x": 0.59, "y": 0.38, "abbr": "LA2", "size": 0.048},

    # ── Heel (3 sensors) - LARGE ───────────────────────────────────────────
    13: {"name": "Medial Heel",   "zone": "Heel",       "x": 0.32, "y": 0.16, "abbr": "HM", "size": 0.058},
    14: {"name": "Central Heel",  "zone": "Heel",       "x": 0.45, "y": 0.12, "abbr": "HC", "size": 0.058},
    15: {"name": "Lateral Heel",  "zone": "Heel",       "x": 0.58, "y": 0.16, "abbr": "HL", "size": 0.058},
}

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
                if len(values) == 16:  # 16 sensors
                    data.append(values)
            except:
                continue
    if not data:
        raise ValueError("No valid 16-sensor rows found in file.")
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
        
        # Create array for 16 sensors
        frame = np.zeros(16)
        
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
        frame[8] = int(280 + 130 * forefoot_bias + np.random.randint(-25, 25))  # M4-5 (combined)
        
        # 9-12: Midfoot / Arch (4 sensors)
        frame[9] = int(70 + 40 * np.random.random() + 15 * heel_bias)   # MA1
        frame[10] = int(65 + 35 * np.random.random() + 10 * heel_bias)  # MA2
        frame[11] = int(60 + 30 * np.random.random() + 10 * heel_bias)  # LA1
        frame[12] = int(55 + 25 * np.random.random() + 5 * heel_bias)   # LA2
        
        # 13-15: Heel (3 sensors)
        frame[13] = int(480 + 300 * heel_bias + np.random.randint(-50, 50))  # Medial Heel
        frame[14] = int(450 + 270 * heel_bias + np.random.randint(-45, 45))  # Central Heel
        frame[15] = int(400 + 240 * heel_bias + np.random.randint(-40, 40))  # Lateral Heel
        
        data.append(np.clip(frame, 0, 1023))
    return np.array(data)

# =============================================================================
# CLINICAL ANALYSIS
# =============================================================================

def analyze_frame(frame):
    s = frame
    # 16 sensors: 0=BigToe, 1-4=Toes, 5-8=Metatarsal, 9-12=Midfoot, 13-15=Heel
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
    total_sum = np.sum(frame)
    zone_pct = {z: (zone_sum[z] / total_sum * 100) if total_sum > 0 else 0
                for z in zones}

    # Medial = big toe + M1 + medial arch + medial heel
    # Lateral = lateral toes + M4 + lateral arch + lateral heel
    medial_indices = [0, 5, 9, 10, 13]
    lateral_indices = [4, 8, 11, 12, 15]
    
    medial  = np.mean(s[medial_indices])
    lateral = np.mean(s[lateral_indices])
    ml_ratio = medial / (lateral + 1e-6)

    forefoot = np.mean(s[[0, 1, 2, 3, 4, 5, 6, 7, 8]])
    heel     = np.mean(s[[13, 14, 15]])
    fh_ratio = forefoot / (heel + 1e-6)

    arch_avg      = zone_avg["Midfoot"]
    arch_load_pct = zone_pct["Midfoot"]

    if arch_avg < 80:
        flat_foot = "Normal Arch";        flat_foot_risk = 0
    elif arch_avg < 150:
        flat_foot = "Mild Flat Foot";     flat_foot_risk = 1
    elif arch_avg < 250:
        flat_foot = "Moderate Flat Foot"; flat_foot_risk = 2
    else:
        flat_foot = "Severe Flat Foot";   flat_foot_risk = 3

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
        "max_pressure": np.max(frame),
        "mean_pressure": np.mean(frame),
        "total_load": np.sum(frame),
    }

# =============================================================================
# FOOT OUTLINE  (smooth Bezier body + 5 toe ellipses)
# Returns (body_patch, list_of_toe_patches)
# =============================================================================

def draw_foot_outline(ax, alpha=0.10):
    # ── Main foot body ──────────────────────────────────────────────────────
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

    codes = [Path.MOVETO] + [Path.CURVE4] * (len(verts) - 1)
    assert (len(verts) - 1) % 3 == 0, "CURVE4 vert count error"

    path = Path(verts, codes)
    body_patch = patches.PathPatch(
        path, facecolor='#f3e3c3', edgecolor='#8B6914',
        lw=1.5, alpha=alpha, zorder=0
    )
    ax.add_patch(body_patch)

    # ── Individual toe ellipses ─────────────────────────────────────────────
    toe_defs = [
        (0.30, 0.935, 0.075, 0.062),  # Hallux (big toe)
        (0.46, 0.915, 0.052, 0.048),  # Toe 2
        (0.58, 0.885, 0.046, 0.042),  # Toe 3
        (0.68, 0.855, 0.040, 0.036),  # Toe 4
        (0.77, 0.825, 0.035, 0.030),  # Toe 5 (little)
    ]
    toe_patches = []
    for (cx, cy, rx, ry) in toe_defs:
        ellipse = Ellipse(
            (cx, cy), width=rx * 2, height=ry * 2,
            facecolor='#f3e3c3', edgecolor='#8B6914',
            lw=1.5, alpha=alpha, zorder=0
        )
        ax.add_patch(ellipse)
        toe_patches.append(ellipse)

    return body_patch, toe_patches


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

    # ── Figure layout ────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(20, 13), facecolor='#0d1117')
    gs = GridSpec(3, 4, figure=fig,
                  left=0.04, right=0.96, top=0.92, bottom=0.05,
                  wspace=0.35, hspace=0.40,
                  width_ratios=[1.6, 1, 1, 1])

    fig.suptitle(
        f"FOOT PRESSURE ANALYSIS  ·  Frame {frame_idx + 1}/{len(data)}",
        fontsize=17, fontweight='bold', color='white', y=0.97
    )

    # ── Panel 1: Anatomical Foot Heatmap ─────────────────────────────────────
    ax_foot = fig.add_subplot(gs[:, 0])
    ax_foot.set_facecolor('#0d1117')
    ax_foot.set_xlim(0, 1)
    ax_foot.set_ylim(0, 1.08)
    ax_foot.set_aspect('equal')
    ax_foot.axis('off')
    ax_foot.set_title("PRESSURE MAP", color='white', fontsize=13,
                       fontweight='bold', pad=12)

    # Build Gaussian heatmap grid - adjusted for larger sensors
    grid_size = 300
    xs = np.linspace(0, 1, grid_size)
    ys = np.linspace(0, 1.08, grid_size)
    XX, YY = np.meshgrid(xs, ys)

    vmax = max(np.max(frame), 1)
    heatmap = np.zeros((grid_size, grid_size))
    for idx, sinfo in SENSORS.items():
        val = frame[idx]
        sx, sy = sinfo['x'], sinfo['y']
        # Larger sigma for bigger sensors
        sigma = 0.06  # Increased from 0.04 for larger sensor footprint
        blob = np.exp(-((XX - sx)**2 + (YY - sy)**2) / (2 * sigma**2))
        heatmap += blob * val

    heatmap_norm = heatmap / (np.max(heatmap) + 1e-6)

    # Draw foot outline
    body_patch, toe_patches = draw_foot_outline(ax_foot, alpha=0.12)

    # Main heatmap
    im = ax_foot.imshow(
        heatmap_norm,
        origin='lower',
        extent=[0, 1, 0, 1.08],
        cmap=PRESSURE_CMAP,
        alpha=0.88,
        vmin=0, vmax=1,
        zorder=2,
        aspect='auto'
    )
    im.set_clip_path(body_patch)

    # Toe heatmaps
    for toe_patch in toe_patches:
        im_toe = ax_foot.imshow(
            heatmap_norm,
            origin='lower',
            extent=[0, 1, 0, 1.08],
            cmap=PRESSURE_CMAP,
            alpha=0.88,
            vmin=0, vmax=1,
            zorder=2,
            aspect='auto'
        )
        im_toe.set_clip_path(toe_patch)

    # Redraw outline
    draw_foot_outline(ax_foot, alpha=0.30)

    # Sensor dots + labels - LARGE for Velostat
    for idx, sinfo in SENSORS.items():
        val = frame[idx]
        norm_val = val / vmax
        col = pressure_to_color(val, 0, vmax)

        # Use LARGE predefined size for bigger Velostat sensors
        base_size = sinfo.get('size', 0.050)
        r = base_size * (0.9 + 0.2 * norm_val)
        
        circle = plt.Circle((sinfo['x'], sinfo['y']), r,
                              color=col, alpha=0.92,
                              ec='white', linewidth=2.0, zorder=5)
        ax_foot.add_patch(circle)

        # Abbreviation with background - larger font
        ax_foot.text(sinfo['x'], sinfo['y'], sinfo['abbr'],
                     ha='center', va='center', fontsize=10,
                     fontweight='bold', color='white', zorder=6,
                     bbox=dict(boxstyle='round,pad=0.2', facecolor='#000000', alpha=0.6))
        
        # Pressure value - larger font, positioned lower for big sensors
        ax_foot.text(sinfo['x'], sinfo['y'] - r - 0.030, f"{int(val)}",
                     ha='center', va='top', fontsize=8,
                     color='#ffffff', fontweight='bold', zorder=6)

    # Zone labels
    zone_y = {"Big Toe": 0.95, "Toes": 0.84, "Metatarsal": 0.67,
               "Midfoot": 0.49, "Heel": 0.16}
    for zone, zy in zone_y.items():
        ax_foot.text(-0.04, zy, zone, ha='right', va='center',
                     fontsize=8, color=ZONE_COLORS[zone], fontweight='bold')
        ax_foot.annotate('', xy=(0.08, zy), xytext=(-0.02, zy),
                          arrowprops=dict(arrowstyle='->', color=ZONE_COLORS[zone], lw=1.2))

    # Colorbar
    cbar = plt.colorbar(im, ax=ax_foot, orientation='vertical',
                         fraction=0.035, pad=0.02)
    cbar.set_label('Pressure (ADC units)', color='white', fontsize=9)
    cbar.ax.yaxis.set_tick_params(color='white', labelcolor='white')
    cbar.set_ticks([0, 0.25, 0.5, 0.75, 1.0])
    cbar.set_ticklabels(['0', f'{int(vmax*0.25)}', f'{int(vmax*0.5)}',
                          f'{int(vmax*0.75)}', f'{int(vmax)}'])

    # ── Panel 2: Weight Distribution ───────────────────────────────────
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

    legend_patches = [mpatches.Patch(color=ZONE_COLORS[z],
                                      label=f"{z}: {pcts[i]:.1f}%")
                      for i, z in enumerate(zones_ordered)]
    ax_donut.legend(handles=legend_patches, loc='lower center',
                    bbox_to_anchor=(0.5, -0.35), fontsize=7.5,
                    facecolor='#1a1f2e', edgecolor='gray',
                    labelcolor='white', framealpha=0.8)

    # ── Panel 3: Medial-Lateral Balance ──────────────────────────────────────
    ax_ml = fig.add_subplot(gs[0, 2])
    ax_ml.set_facecolor('#161b25')

    medial_pct  = res['medial'] / (res['medial'] + res['lateral'] + 1e-6) * 100
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
                fontsize=9, fontweight='bold')

    # ── Panel 4: Forefoot vs Heel ─────────────────────────────────────────────
    ax_fh = fig.add_subplot(gs[0, 3])
    ax_fh.set_facecolor('#161b25')

    ff_pct = sum(res['zone_pct'][z] for z in ["Big Toe", "Toes", "Metatarsal"])
    h_pct  = sum(res['zone_pct'][z] for z in ["Midfoot", "Heel"])

    ax_fh.bar(['Forefoot', 'Hindfoot'], [ff_pct, h_pct],
               color=['#FF8800', '#4488FF'], edgecolor='white', linewidth=0.5)
    ax_fh.axhline(50, color='white', linewidth=1, linestyle='--', alpha=0.5)
    ax_fh.set_ylim(0, 100)
    ax_fh.set_ylabel('%', color='white', fontsize=9)
    ax_fh.set_title("FOREFOOT /\nHINDFOOT %", color='white',
                     fontsize=10, fontweight='bold')
    ax_fh.tick_params(colors='white')
    for spine in ax_fh.spines.values():
        spine.set_edgecolor('#333')
    for i, val in enumerate([ff_pct, h_pct]):
        ax_fh.text(i, val + 1.5, f'{val:.1f}%', ha='center',
                   color='white', fontsize=10, fontweight='bold')

    # ── Panel 5: Arch / Flat Foot ─────────────────────────────────────────────
    ax_arch = fig.add_subplot(gs[1, 1:3])
    ax_arch.set_facecolor('#161b25')

    arch_names = ["Med Arch 1", "Med Arch 2", "Lat Arch 1", "Lat Arch 2"]
    arch_vals  = [frame[9], frame[10], frame[11], frame[12]]
    arch_colors = []
    for v in arch_vals:
        if   v < 80:  arch_colors.append('#44BB44')
        elif v < 150: arch_colors.append('#FFD700')
        elif v < 250: arch_colors.append('#FF8800')
        else:         arch_colors.append('#FF3333')

    bars = ax_arch.bar(arch_names, arch_vals, color=arch_colors,
                        edgecolor='white', linewidth=0.5, width=0.6)
    ax_arch.axhline(80, color='#44BB44', linewidth=1.2, linestyle='--',
                     alpha=0.7, label='Normal threshold')
    ax_arch.axhline(150, color='#FFD700', linewidth=1.2, linestyle='--',
                     alpha=0.7, label='Mild flat foot')
    ax_arch.axhline(250, color='#FF3333', linewidth=1.2, linestyle='--',
                     alpha=0.7, label='Moderate flat foot')
    ax_arch.set_ylim(0, max(400, max(arch_vals) * 1.2))
    ax_arch.set_title(
        f"ARCH / FLAT FOOT EVALUATION  —  {res['flat_foot']}  "
        f"(Arch load: {res['arch_load_pct']:.1f}%)",
        color='white', fontsize=10, fontweight='bold'
    )
    ax_arch.tick_params(colors='white')
    ax_arch.set_facecolor('#161b25')
    for spine in ax_arch.spines.values():
        spine.set_edgecolor('#333')
    ax_arch.legend(fontsize=7.5, facecolor='#1a1f2e',
                   edgecolor='gray', labelcolor='white', loc='upper right')
    for bar, val in zip(bars, arch_vals):
        ax_arch.text(bar.get_x() + bar.get_width()/2, val + 8,
                     f'{int(val)}', ha='center', color='white', fontsize=8, fontweight='bold')

    ff_badge_color = ['#44BB44', '#FFD700', '#FF8800', '#FF3333'][res['flat_foot_risk']]
    ax_arch.text(3.2, max(arch_vals) * 0.9, res['flat_foot'],
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

    ax_diab.text(0.5, 0.12,
                 f"Hallux: {int(frame[0])}   Met 1: {int(frame[5])}",
                 ha='center', color='#cccccc', fontsize=8.5)
    ax_diab.text(0.5, 0.04, "(Primary diabetic ulcer sites)",
                 ha='center', color='gray', fontsize=7.5, style='italic')

    # ── Panel 7: Metatarsal Profile ───────────────────────────────────────────
    ax_met = fig.add_subplot(gs[2, 1:3])
    ax_met.set_facecolor('#161b25')

    met_vals  = [frame[5], frame[6], frame[7], frame[8]]
    met_names = ['Met 1\n(Medial)', 'Met 2', 'Met 3', 'Met 4-5\n(Lateral)']
    met_colors = [pressure_to_color(v, 0, vmax) for v in met_vals]

    bars = ax_met.bar(met_names, met_vals, color=met_colors,
                       edgecolor='white', linewidth=0.5, width=0.6)
    ax_met.set_title("METATARSAL HEAD PRESSURE PROFILE", color='white',
                      fontsize=10, fontweight='bold')
    ax_met.tick_params(colors='white', labelsize=8)
    ax_met.set_facecolor('#161b25')
    ax_met.set_ylabel('Pressure', color='white', fontsize=9)
    for spine in ax_met.spines.values():
        spine.set_edgecolor('#333')
    for bar, val in zip(bars, met_vals):
        ax_met.text(bar.get_x() + bar.get_width()/2, val + 8,
                    f'{int(val)}', ha='center', color='white', fontsize=8, fontweight='bold')
    ax_met.axhline(600, color='#FF4444', linewidth=1.5, linestyle='--',
                    alpha=0.7, label='Diabetic risk threshold')
    ax_met.legend(fontsize=8, facecolor='#1a1f2e',
                  edgecolor='gray', labelcolor='white')

    # ── Panel 8: Clinical Summary ─────────────────────────────────────────────
    ax_sum = fig.add_subplot(gs[2, 3])
    ax_sum.set_facecolor('#161b25')
    ax_sum.axis('off')
    ax_sum.set_title("CLINICAL\nSUMMARY", color='white',
                      fontsize=10, fontweight='bold')

    summary_lines = [
        ("Peak Pressure",  f"{int(res['max_pressure'])}"),
        ("Mean Pressure",  f"{res['mean_pressure']:.1f}"),
        ("Arch Status",    res['flat_foot']),
        ("Diabetic Risk",  res['diabetic_risk']),
        ("M/L Ratio",      f"{res['ml_ratio']:.2f}"),
        ("F/H Ratio",      f"{res['fh_ratio']:.2f}"),
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

    if save:
        plt.savefig(f'foot_heatmap_frame_{frame_idx}.png',
                    dpi=150, bbox_inches='tight', facecolor='#0d1117')
        print(f"Saved: foot_heatmap_frame_{frame_idx}.png")

    plt.show()
    return res

# =============================================================================
# TREND PLOT
# =============================================================================

def plot_trends(data):
    all_res = [analyze_frame(f) for f in data]
    frames  = np.arange(len(data))

    fig, axes = plt.subplots(3, 1, figsize=(16, 10), facecolor='#0d1117', sharex=True)
    fig.suptitle("FOOT PRESSURE TRENDS — All Frames",
                  color='white', fontsize=14, fontweight='bold')

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

    ax = axes[1]
    ax.set_facecolor('#161b25')
    arch_avgs = [r['zone_avg']['Midfoot'] for r in all_res]
    ax.fill_between(frames, arch_avgs, color='#44BB44', alpha=0.4)
    ax.plot(frames, arch_avgs, color='#44BB44', linewidth=2, label='Arch Pressure')
    ax.axhline(80, color='#FFD700', linewidth=1, linestyle='--', label='Mild flat foot')
    ax.axhline(150, color='#FF8800', linewidth=1, linestyle='--', label='Moderate flat foot')
    ax.axhline(250, color='#FF3333', linewidth=1, linestyle='--', label='Severe flat foot')
    ax.set_ylabel('Arch Pressure', color='white', fontsize=9)
    ax.set_title('Arch Load — Flat Foot Indicator', color='white', fontsize=10)
    ax.legend(fontsize=8, facecolor='#1a1f2e', labelcolor='white',
               edgecolor='gray', loc='upper right')
    ax.tick_params(colors='white')
    for s in ax.spines.values(): s.set_edgecolor('#333')

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
    print("Saved: foot_trends.png")
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
    try:
        data = load_data("foot_data.txt")
    except (FileNotFoundError, ValueError) as e:
        print(f"Note: {e}\nUsing generated sample data.")
        data = generate_sample_data(80)

    print(f"\n{'='*50}")
    print(f"  LARGE VELOSTAT FOOT PRESSURE SYSTEM - 16 SENSORS")
    print(f"{'='*50}")
    print(f"  Sensor count  : 16")
    print(f"    • Big Toe     : 1 sensor (55mm diameter)")
    print(f"    • Toes        : 4 sensors (44-50mm diameter)")
    print(f"    • Metatarsals : 4 sensors (54-60mm diameter)")
    print(f"    • Midfoot     : 4 sensors (48mm diameter)")
    print(f"    • Heel        : 3 sensors (58mm diameter)")
    print(f"  Frames        : {len(data)}")
    print(f"  Pressure range: {int(np.min(data))} – {int(np.max(data))}")
    print(f"  Sensor size   : ~20-25mm actual physical size (LARGE Velostat)")
    print(f"{'='*50}\n")

    res = plot_heatmap(frame_idx=-1, data=data, save=True)
    print_report(res, len(data) - 1)

    plot_trends(data)

    all_res = [analyze_frame(f) for f in data]
    print("\nSESSION SUMMARY")
    print(f"  Avg arch pressure              : {np.mean([r['zone_avg']['Midfoot'] for r in all_res]):.1f}")
    print(f"  Frames with flat foot (mod+)   : {sum(1 for r in all_res if r['flat_foot_risk'] >= 2)}/{len(data)}")
    print(f"  Frames with High Diabetic Risk : {sum(1 for r in all_res if r['diabetic_risk'] == 'High Risk')}/{len(data)}")