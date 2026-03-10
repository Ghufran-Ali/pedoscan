# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 14:07:19 2026

@author: Ghufran
"""

# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# from matplotlib.animation import FuncAnimation

# # Load the saved file
# data = []
# with open("foot_data.txt", "r") as f:
#     for line in f:
#         if not line.strip() or not line[0].isdigit():
#             continue
#         values = line.strip().split(',')
#         if len(values) == 12:
#             data.append(list(map(int, values)))

# data = np.array(data)
# print(f"Data shape: {data.shape}")

# # Prepare the figure
# fig, ax = plt.subplots()
# foot_matrix = data[0].reshape(3,4)
# heatmap = sns.heatmap(foot_matrix, cmap='jet', vmin=0, vmax=1023, annot=True, ax=ax)
# ax.set_title("Foot Pressure Map (Frame 1)")

# # Update function for animation
# def update(frame_index):
#     ax.clear()  # clear previous frame
#     foot_matrix = data[frame_index].reshape(3,4)
#     sns.heatmap(foot_matrix, cmap='jet', vmin=0, vmax=1023, annot=True, ax=ax)
#     ax.set_title(f"Foot Pressure Map (Frame {frame_index+1})")

# # Create animations
# ani = FuncAnimation(fig, update, frames=len(data), interval=300)  # 300ms per frame
# plt.show()


# -*- coding: utf-8 -*-
# """
# Foot Pressure Assessment System (Pedoscan-like)
# Author: Ghufran
# """

# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# from matplotlib.animation import FuncAnimation
# from matplotlib.gridspec import GridSpec
# import matplotlib.patches as mpatches
# from scipy import ndimage
# import warnings
# warnings.filterwarnings('ignore')

# # =============================================================================
# # LOAD AND PREPARE DATA
# # =============================================================================

# def load_foot_data(filename="foot_data.txt"):
#     """Load foot pressure data from text file"""
#     data = []
#     with open(filename, "r") as f:
#         for line in f:
#             # Skip comment lines and empty lines
#             line = line.strip()
#             if not line or line.startswith('#') or line.startswith('Dual'):
#                 continue
            
#             # Try to parse the line
#             try:
#                 values = line.split(',')
#                 if len(values) == 12:
#                     data.append(list(map(int, values)))
#             except:
#                 continue
    
#     data = np.array(data)
#     print(f"Loaded {len(data)} frames of foot pressure data")
#     print(f"Data shape: {data.shape} (frames × sensors)")
#     return data

# # Load the data
# data = load_foot_data("foot_data.txt")

# if len(data) == 0:
#     print("No data loaded! Check file format.")
#     # Create sample data for testing if no file exists
#     print("Creating sample data for demonstration...")
#     data = np.random.randint(200, 800, (60, 12))
#     print(f"Created {len(data)} sample frames")

# # =============================================================================
# # FOOT PRESSURE VISUALIZATION FUNCTIONS
# # =============================================================================

# def create_foot_mask():
#     """Create a foot-shaped mask for the 3x4 sensor grid"""
#     # 3x4 grid representing foot regions
#     mask = np.ones((3, 4))
#     return mask

# def interpolate_foot_pressure(matrix, factor=4):
#     """Interpolate the 3x4 grid to a smoother foot-shaped image"""
#     # Convert to float for interpolation
#     matrix_float = matrix.astype(float)
    
#     # Upsample the matrix for smoother visualization
#     zoom_factor = (factor, factor)
#     interpolated = ndimage.zoom(matrix_float, zoom_factor, order=1)  # Bilinear interpolation
    
#     # Apply circular mask for foot shape (approximate)
#     y, x = np.ogrid[:interpolated.shape[0], :interpolated.shape[1]]
#     center_y, center_x = interpolated.shape[0]/2, interpolated.shape[1]/2
    
#     # Create elliptical mask (foot-shaped)
#     mask_y = ((y - center_y) / (interpolated.shape[0]/2.2)) ** 2
#     mask_x = ((x - center_x) / (interpolated.shape[1]/2.5)) ** 2
#     mask = mask_y + mask_x <= 1
    
#     # Create masked array instead of assigning NaN
#     interpolated_masked = np.ma.masked_where(~mask, interpolated)
    
#     return interpolated_masked

# def calculate_pressure_metrics(frame_data):
#     """Calculate various pressure metrics for a frame"""
#     metrics = {}
    
#     # Basic statistics
#     metrics['max'] = np.max(frame_data)
#     metrics['min'] = np.min(frame_data)
#     metrics['mean'] = np.mean(frame_data)
#     metrics['std'] = np.std(frame_data)
#     metrics['total'] = np.sum(frame_data)
    
#     # Regional analysis (3x4 grid regions)
#     matrix = frame_data.reshape(3, 4)
    
#     # Heel region (bottom row)
#     metrics['heel_mean'] = np.mean(matrix[2, :])
#     metrics['heel_max'] = np.max(matrix[2, :])
    
#     # Midfoot region (middle row)
#     metrics['midfoot_mean'] = np.mean(matrix[1, :])
#     metrics['midfoot_max'] = np.max(matrix[1, :])
    
#     # Forefoot/toe region (top row)
#     metrics['forefoot_mean'] = np.mean(matrix[0, :])
#     metrics['forefoot_max'] = np.max(matrix[0, :])
    
#     # Left/Right balance
#     metrics['left_mean'] = np.mean(matrix[:, 0:2])
#     metrics['right_mean'] = np.mean(matrix[:, 2:4])
#     metrics['balance_ratio'] = metrics['left_mean'] / (metrics['right_mean'] + 1)  # Avoid div by zero
    
#     # Pressure distribution classification
#     if metrics['max'] < 200:
#         metrics['category'] = 'Very Light'
#         metrics['color'] = 'blue'
#     elif metrics['max'] < 400:
#         metrics['category'] = 'Light'
#         metrics['color'] = 'green'
#     elif metrics['max'] < 600:
#         metrics['category'] = 'Moderate'
#         metrics['color'] = 'yellow'
#     elif metrics['max'] < 800:
#         metrics['category'] = 'High'
#         metrics['color'] = 'orange'
#     else:
#         metrics['category'] = 'Very High'
#         metrics['color'] = 'red'
    
#     return metrics

# # =============================================================================
# # STATIC FOOT PRESSURE VISUALIZATION (Single Frame)
# # =============================================================================

# def plot_foot_pressure_assessment(frame_idx=-1, save=False):
#     """Create comprehensive foot pressure assessment plot"""
    
#     # Get the frame data
#     if frame_idx == -1:
#         frame_idx = len(data) - 1
#         frame_data = data[frame_idx]
#     else:
#         frame_data = data[frame_idx]
    
#     # Reshape to 3x4 grid
#     foot_matrix = frame_data.reshape(3, 4)
    
#     # Calculate metrics
#     metrics = calculate_pressure_metrics(frame_data)
    
#     # Create figure with GridSpec for complex layout
#     fig = plt.figure(figsize=(16, 10))
#     gs = GridSpec(3, 3, figure=fig, width_ratios=[1.5, 1, 1], height_ratios=[1, 1, 1])
    
#     # Main foot pressure heatmap
#     ax1 = fig.add_subplot(gs[:, 0])
    
#     # Create smooth interpolated heatmap
#     smooth_matrix = interpolate_foot_pressure(foot_matrix, factor=8)
    
#     # Use imshow with masked array
#     im = ax1.imshow(smooth_matrix, cmap='jet', vmin=0, vmax=1023, aspect='auto', 
#                     interpolation='gaussian')
    
#     # Overlay sensor positions
#     for i in range(3):
#         for j in range(4):
#             # Calculate position in the interpolated image
#             y_pos = int((i + 0.5) * smooth_matrix.shape[0] / 3)
#             x_pos = int((j + 0.5) * smooth_matrix.shape[1] / 4)
#             value = foot_matrix[i, j]
            
#             # Color code based on pressure
#             if value < 200:
#                 color = 'darkblue'
#                 bg_color = 'lightblue'
#             elif value < 400:
#                 color = 'darkgreen'
#                 bg_color = 'lightgreen'
#             elif value < 600:
#                 color = 'darkorange'
#                 bg_color = 'yellow'
#             elif value < 800:
#                 color = 'darkred'
#                 bg_color = 'orange'
#             else:
#                 color = 'white'
#                 bg_color = 'red'
            
#             ax1.text(x_pos, y_pos, f'{value}', 
#                     ha='center', va='center', 
#                     fontsize=10, fontweight='bold',
#                     color=color, bbox=dict(boxstyle='round,pad=0.3', 
#                                           facecolor=bg_color, alpha=0.8, 
#                                           edgecolor=color))
    
#     ax1.set_title(f'Foot Pressure Map - Frame {frame_idx}', fontsize=14, fontweight='bold')
#     ax1.axis('off')
    
#     # Add foot region labels
#     ax1.text(smooth_matrix.shape[1]//2, smooth_matrix.shape[0]//6, 
#              'TOES', ha='center', fontsize=12, fontweight='bold', 
#              color='white', bbox=dict(boxstyle='round', facecolor='black', alpha=0.5))
#     ax1.text(smooth_matrix.shape[1]//2, smooth_matrix.shape[0]//2, 
#              'MIDFOOT', ha='center', fontsize=12, fontweight='bold',
#              color='white', bbox=dict(boxstyle='round', facecolor='black', alpha=0.5))
#     ax1.text(smooth_matrix.shape[1]//2, smooth_matrix.shape[0]*5//6, 
#              'HEEL', ha='center', fontsize=12, fontweight='bold',
#              color='white', bbox=dict(boxstyle='round', facecolor='black', alpha=0.5))
    
#     # Colorbar
#     cbar = plt.colorbar(im, ax=ax1, fraction=0.046, pad=0.04)
#     cbar.set_label('Pressure (0-1023)', fontsize=12)
    
#     # Pressure metrics panel
#     ax2 = fig.add_subplot(gs[0, 1])
#     ax2.axis('off')
#     ax2.set_title('PRESSURE METRICS', fontsize=14, fontweight='bold', color='darkblue')
    
#     metrics_text = [
#         f"Maximum: {metrics['max']}",
#         f"Minimum: {metrics['min']}",
#         f"Average: {metrics['mean']:.1f}",
#         f"Std Dev: {metrics['std']:.1f}",
#         f"Total Load: {metrics['total']}",
#         f"Category: {metrics['category']}"
#     ]
    
#     for i, text in enumerate(metrics_text):
#         ax2.text(0.1, 0.85 - i*0.12, text, fontsize=11, 
#                 transform=ax2.transAxes,
#                 bbox=dict(boxstyle='round,pad=0.5', facecolor=metrics['color'], alpha=0.2,
#                          edgecolor=metrics['color']))
    
#     # Regional analysis panel
#     ax3 = fig.add_subplot(gs[1, 1])
#     ax3.axis('off')
#     ax3.set_title('🦶 REGIONAL ANALYSIS', fontsize=14, fontweight='bold', color='darkgreen')
    
#     regional_text = [
#         f"Forefoot (Avg): {metrics['forefoot_mean']:.1f}",
#         f"Forefoot (Max): {metrics['forefoot_max']}",
#         f"Midfoot (Avg): {metrics['midfoot_mean']:.1f}",
#         f"Midfoot (Max): {metrics['midfoot_max']}",
#         f"Heel (Avg): {metrics['heel_mean']:.1f}",
#         f"Heel (Max): {metrics['heel_max']}"
#     ]
    
#     for i, text in enumerate(regional_text):
#         ax3.text(0.1, 0.8 - i*0.1, text, fontsize=10,
#                 transform=ax3.transAxes,
#                 bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.3))
    
#     # Balance analysis panel
#     ax4 = fig.add_subplot(gs[2, 1])
#     ax4.axis('off')
#     ax4.set_title('⚖️ BALANCE ANALYSIS', fontsize=14, fontweight='bold', color='darkred')
    
#     # Calculate balance percentage
#     total_balance = metrics['left_mean'] + metrics['right_mean']
#     if total_balance > 0:
#         left_percent = (metrics['left_mean'] / total_balance) * 100
#         right_percent = (metrics['right_mean'] / total_balance) * 100
#     else:
#         left_percent = right_percent = 50
    
#     ax4.text(0.1, 0.7, f"Left Side Avg: {metrics['left_mean']:.1f}", 
#             fontsize=11, transform=ax4.transAxes)
#     ax4.text(0.1, 0.5, f"Right Side Avg: {metrics['right_mean']:.1f}", 
#             fontsize=11, transform=ax4.transAxes)
    
#     # Balance bar
#     bar_ax = ax4.inset_axes([0.1, 0.2, 0.8, 0.2])
#     bar_ax.barh(0, left_percent, color='blue', alpha=0.7, label=f'Left {left_percent:.0f}%')
#     bar_ax.barh(0, right_percent, left=left_percent, color='red', alpha=0.7, 
#                label=f'Right {right_percent:.0f}%')
#     bar_ax.set_xlim(0, 100)
#     bar_ax.set_ylim(-0.5, 0.5)
#     bar_ax.axis('off')
#     bar_ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=8)
    
#     # Time series panel
#     ax5 = fig.add_subplot(gs[:, 2])
    
#     # Plot pressure over time for key regions
#     frames_to_plot = min(50, len(data))
#     frame_indices = np.arange(max(0, len(data)-frames_to_plot), len(data))
    
#     # Calculate regional averages over time
#     heel_avg = [np.mean(d.reshape(3, 4)[2, :]) for d in data[-frames_to_plot:]]
#     midfoot_avg = [np.mean(d.reshape(3, 4)[1, :]) for d in data[-frames_to_plot:]]
#     forefoot_avg = [np.mean(d.reshape(3, 4)[0, :]) for d in data[-frames_to_plot:]]
    
#     ax5.plot(range(len(heel_avg)), heel_avg, 'r-', linewidth=2, label='Heel', alpha=0.8)
#     ax5.plot(range(len(midfoot_avg)), midfoot_avg, 'g-', linewidth=2, label='Midfoot', alpha=0.8)
#     ax5.plot(range(len(forefoot_avg)), forefoot_avg, 'b-', linewidth=2, label='Forefoot', alpha=0.8)
    
#     ax5.set_xlabel('Frame (recent history)', fontsize=11)
#     ax5.set_ylabel('Pressure', fontsize=11)
#     ax5.set_title('PRESSURE TRENDS', fontsize=14, fontweight='bold', color='purple')
#     ax5.legend(loc='upper right', fontsize=9)
#     ax5.grid(True, alpha=0.3)
    
#     plt.suptitle(f'FOOT PRESSURE ASSESSMENT - {metrics["category"].upper()} PRESSURE PATTERN', 
#                 fontsize=16, fontweight='bold', y=0.98)
#     plt.tight_layout()
    
#     if save:
#         plt.savefig(f'foot_pressure_frame_{frame_idx}.png', dpi=150, bbox_inches='tight')
    
#     plt.show()
    
#     # Print clinical summary
#     print("\n" + "="*60)
#     print("CLINICAL FOOT PRESSURE SUMMARY")
#     print("="*60)
#     print(f"Assessment: {metrics['category']} Pressure Pattern")
#     print(f"Peak Pressure: {metrics['max']} (Location: {get_peak_location(foot_matrix)})")
#     print(f"Pressure Distribution: {get_distribution_description(metrics)}")
    
#     # Balance description
#     if left_percent > 55:
#         balance_desc = "Left Foot Dominant"
#     elif right_percent > 55:
#         balance_desc = "Right Foot Dominant"
#     else:
#         balance_desc = "Well Balanced"
    
#     print(f"Balance: {balance_desc} (L:{left_percent:.0f}% / R:{right_percent:.0f}%)")
#     print("="*60)

# def get_peak_location(matrix):
#     """Find location of peak pressure"""
#     max_idx = np.argmax(matrix)
#     row, col = max_idx // 4, max_idx % 4
    
#     regions = ['Forefoot', 'Midfoot', 'Heel']
#     sides = ['Inner', 'Outer']
    
#     region = regions[row]
#     side = sides[0] if col < 2 else sides[1]
    
#     return f"{region} ({side})"

# def get_distribution_description(metrics):
#     """Generate clinical description of pressure distribution"""
#     if metrics['std'] < 20:
#         return "Very Even Distribution"
#     elif metrics['std'] < 50:
#         return "Even Distribution"
#     elif metrics['std'] < 100:
#         return "Moderately Uneven"
#     else:
#         return "Highly Concentrated"

# # =============================================================================
# # RUN THE ANALYSIS
# # =============================================================================

# if __name__ == "__main__":
    
#     print("\n" + "="*60)
#     print("FOOT PRESSURE ASSESSMENT SYSTEM (PEDOSCAN-STYLE)")
#     print("="*60)
    
#     # Show basic info
#     print(f"\n Dataset contains {len(data)} frames of foot pressure data")
#     print(f" Sensor grid: 3×4 (12 sensors)")
#     print(f"Pressure range: {np.min(data)} - {np.max(data)}")
    
#     # Plot the last frame with full assessment
#     plot_foot_pressure_assessment(frame_idx=-1, save=True)
    
#     # Show summary statistics
#     print("\n" + "="*60)
#     print("OVERALL STATISTICS")
#     print("="*60)
    
#     all_metrics = [calculate_pressure_metrics(frame) for frame in data]
    
#     print(f"Average peak pressure: {np.mean([m['max'] for m in all_metrics]):.1f}")
#     print(f"Average pressure: {np.mean([m['mean'] for m in all_metrics]):.1f}")
    
#     # Find most common category
#     categories = [m['category'] for m in all_metrics]
#     most_common = max(set(categories), key=categories.count)
#     print(f"Most common pattern: {most_common}")
    
#     print("\nAnalysis complete!")

# -*- coding: utf-8 -*-
"""
Professional Foot Pressure Assessment System (Pedoscan-style)
Author: Ghufran
Based on 12-sensor anatomical foot mapping
"""

# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# from matplotlib.gridspec import GridSpec
# from matplotlib.patches import Rectangle, Circle, Polygon
# from scipy import ndimage
# import warnings
# warnings.filterwarnings('ignore')

# # =============================================================================
# # ANATOMICAL FOOT MAPPING (12 SENSORS)
# # =============================================================================

# # Sensor mapping based on actual foot anatomy
# FOOT_REGIONS = {
#     # FOREFOOT (Top row - 4 sensors)
#     0:  {"name": "Big Toe", "region": "Forefoot", "row": 0, "col": 0},
#     1:  {"name": "2nd-3rd Toes", "region": "Forefoot", "row": 0, "col": 1},
#     2:  {"name": "4th-5th Toes", "region": "Forefoot", "row": 0, "col": 2},
#     3:  {"name": "Lateral Forefoot", "region": "Forefoot", "row": 0, "col": 3},
    
#     # METATARSAL (Second row - 4 sensors)
#     4:  {"name": "1st Metatarsal", "region": "Metatarsal", "row": 1, "col": 0},
#     5:  {"name": "2nd-3rd Metatarsal", "region": "Metatarsal", "row": 1, "col": 1},
#     6:  {"name": "4th-5th Metatarsal", "region": "Metatarsal", "row": 1, "col": 2},
#     7:  {"name": "Lateral Metatarsal", "region": "Metatarsal", "row": 1, "col": 3},
    
#     # MIDFOOT/ARCH (Third row - 2 sensors + 2 heel? Let's reorganize)
#     # Actually, let's reorganize to 3x4 grid properly:
#     # Row 0: Forefoot (toes)
#     # Row 1: Metatarsal heads
#     # Row 2: Midfoot/Arch
#     # Row 3: Heel
    
#     # But we have 12 sensors, so 3x4 is fine - let's map properly:
# }

# # Corrected mapping for 3x4 grid (3 rows, 4 columns)
# SENSOR_MAP = {
#     # Row 0: FOREFOOT (Toes)
#     (0, 0): {"zone": "Forefoot", "name": "Hallux (Big Toe)", "abbr": "BT", "risk": "High"},
#     (0, 1): {"zone": "Forefoot", "name": "2nd-3rd Toes", "abbr": "23T", "risk": "Medium"},
#     (0, 2): {"zone": "Forefoot", "name": "4th-5th Toes", "abbr": "45T", "risk": "Medium"},
#     (0, 3): {"zone": "Forefoot", "name": "Lateral Forefoot", "abbr": "LFF", "risk": "Low"},
    
#     # Row 1: METATARSAL HEADS
#     (1, 0): {"zone": "Metatarsal", "name": "1st Metatarsal Head", "abbr": "M1", "risk": "High"},
#     (1, 1): {"zone": "Metatarsal", "name": "2nd-3rd Metatarsal Heads", "abbr": "M23", "risk": "High"},
#     (1, 2): {"zone": "Metatarsal", "name": "4th-5th Metatarsal Heads", "abbr": "M45", "risk": "Medium"},
#     (1, 3): {"zone": "Metatarsal", "name": "Lateral Metatarsal", "abbr": "LM", "risk": "Low"},
    
#     # Row 2: MIDFOOT/ARCH
#     (2, 0): {"zone": "Midfoot", "name": "Medial Arch", "abbr": "MA", "risk": "Low"},
#     (2, 1): {"zone": "Midfoot", "name": "Central Arch", "abbr": "CA", "risk": "Low"},
#     (2, 2): {"zone": "Midfoot", "name": "Lateral Arch", "abbr": "LA", "risk": "Low"},
#     (2, 3): {"zone": "Midfoot", "name": "Lateral Midfoot", "abbr": "LM", "risk": "Low"},
    
#     # Row 3: HEEL (if we had 4 rows, but we have 3x4=12, so heel is included in midfoot? 
#     # Need to adjust - let's move heel to row 3 by reducing midfoot)
# }

# # Better mapping: 4x3 grid would be more anatomical, but we have 12 sensors (3x4)
# # Let's reorganize as 4 rows x 3 columns for better anatomy representation

# # Let's reshape the data as 4x3 instead of 3x4 for better anatomical representation
# # Row 0: Toes (3 sensors)
# # Row 1: Metatarsals (3 sensors)
# # Row 2: Midfoot (3 sensors)
# # Row 3: Heel (3 sensors)

# ANATOMICAL_4X3 = {
#     # Row 0: FOREFOOT (Toes)
#     (0, 0): {"zone": "Forefoot", "name": "Big Toe", "abbr": "BT", "clinical": "Hallux", "risk": "High"},
#     (0, 1): {"zone": "Forefoot", "name": "2nd-3rd Toes", "abbr": "23T", "clinical": "Digits 2-3", "risk": "Medium"},
#     (0, 2): {"zone": "Forefoot", "name": "4th-5th Toes", "abbr": "45T", "clinical": "Digits 4-5", "risk": "Medium"},
    
#     # Row 1: METATARSAL HEADS
#     (1, 0): {"zone": "Metatarsal", "name": "1st Metatarsal", "abbr": "M1", "clinical": "1st Met Head", "risk": "Very High"},
#     (1, 1): {"zone": "Metatarsal", "name": "2nd-3rd Metatarsals", "abbr": "M23", "clinical": "2nd-3rd Met Heads", "risk": "High"},
#     (1, 2): {"zone": "Metatarsal", "name": "4th-5th Metatarsals", "abbr": "M45", "clinical": "4th-5th Met Heads", "risk": "Medium"},
    
#     # Row 2: MIDFOOT/ARCH
#     (2, 0): {"zone": "Midfoot", "name": "Medial Arch", "abbr": "MA", "clinical": "Navicular", "risk": "Low"},
#     (2, 1): {"zone": "Midfoot", "name": "Central Arch", "abbr": "CA", "clinical": "Cuboid", "risk": "Low"},
#     (2, 2): {"zone": "Midfoot", "name": "Lateral Arch", "abbr": "LA", "clinical": "Lateral Midfoot", "risk": "Low"},
    
#     # Row 3: HEEL
#     (3, 0): {"zone": "Heel", "name": "Medial Heel", "abbr": "MH", "clinical": "Medial Calcaneus", "risk": "High"},
#     (3, 1): {"zone": "Heel", "name": "Central Heel", "abbr": "CH", "clinical": "Central Calcaneus", "risk": "High"},
#     (3, 2): {"zone": "Heel", "name": "Lateral Heel", "abbr": "LH", "clinical": "Lateral Calcaneus", "risk": "Medium"},
# }

# # =============================================================================
# # LOAD DATA
# # =============================================================================

# def load_foot_data(filename="foot_data.txt"):
#     """Load foot pressure data from text file"""
#     data = []
#     with open(filename, "r") as f:
#         for line in f:
#             line = line.strip()
#             if not line or line.startswith('#') or line.startswith('Dual'):
#                 continue
#             try:
#                 values = line.split(',')
#                 if len(values) == 12:
#                     data.append(list(map(int, values)))
#             except:
#                 continue
    
#     data = np.array(data)
#     print(f"Loaded {len(data)} frames of foot pressure data")
#     print(f"Data shape: {data.shape} (frames × sensors)")
#     return data

# # Load your data
# try:
#     data = load_foot_data("foot_data.txt")
# except FileNotFoundError:
#     print("foot_data.txt not found. Using sample data.")
#     # Create sample data with anatomical patterns
#     data = []
#     for i in range(60):
#         # Create realistic foot pressure pattern
#         frame = np.zeros(12)
#         # Heel pressure (higher)
#         frame[9:12] = np.random.randint(400, 600, 3)  # Heel
#         # Metatarsal pressure (medium-high)
#         frame[3:6] = np.random.randint(300, 500, 3)   # Metatarsals
#         # Toe pressure (medium)
#         frame[0:3] = np.random.randint(200, 400, 3)   # Toes
#         # Arch pressure (lower)
#         frame[6:9] = np.random.randint(100, 250, 3)   # Arch
#         data.append(frame)
#     data = np.array(data)

# # Reshape data to 4x3 for anatomical view
# def reshape_to_4x3(frame_12):
#     """Reshape 12-sensor data to 4x3 anatomical grid"""
#     # Reorder sensors to match ANATOMICAL_4X3 mapping
#     # Original order might be different - adjust based on your actual sensor layout
#     # This assumes sensors are ordered: Toes(3), Metatarsals(3), Arch(3), Heel(3)
#     return frame_12.reshape(4, 3)

# # =============================================================================
# # PRESSURE ANALYSIS FUNCTIONS
# # =============================================================================

# def analyze_pressure(frame_data):
#     """Comprehensive pressure analysis with clinical relevance"""
    
#     # Reshape to 4x3 anatomical grid
#     foot_4x3 = frame_data.reshape(4, 3)
    
#     results = {
#         # Regional averages
#         "forefoot_avg": np.mean(foot_4x3[0, :]),  # Toes
#         "metatarsal_avg": np.mean(foot_4x3[1, :]),  # Metatarsals
#         "midfoot_avg": np.mean(foot_4x3[2, :]),  # Arch
#         "heel_avg": np.mean(foot_4x3[3, :]),  # Heel
        
#         # Peak pressures by region
#         "forefoot_max": np.max(foot_4x3[0, :]),
#         "metatarsal_max": np.max(foot_4x3[1, :]),
#         "midfoot_max": np.max(foot_4x3[2, :]),
#         "heel_max": np.max(foot_4x3[3, :]),
        
#         # Specific clinical points
#         "big_toe": foot_4x3[0, 0],
#         "first_met": foot_4x3[1, 0],
#         "medial_heel": foot_4x3[3, 0],
#         "lateral_heel": foot_4x3[3, 2],
        
#         # Global metrics
#         "max_pressure": np.max(frame_data),
#         "mean_pressure": np.mean(frame_data),
#         "total_load": np.sum(frame_data),
#         "pressure_variation": np.std(frame_data),
#     }
    
#     # Calculate pressure ratios (clinical indicators)
#     if results["heel_avg"] > 0:
#         results["forefoot_heel_ratio"] = results["forefoot_avg"] / results["heel_avg"]
#     else:
#         results["forefoot_heel_ratio"] = 1.0
    
#     if results["metatarsal_avg"] > 0:
#         results["met_heel_ratio"] = results["metatarsal_avg"] / results["heel_avg"]
#     else:
#         results["met_heel_ratio"] = 1.0
    
#     # Medial-lateral balance
#     medial_pressure = foot_4x3[:, 0].mean()  # Medial column
#     lateral_pressure = foot_4x3[:, 2].mean()  # Lateral column
#     results["medial_lateral_ratio"] = medial_pressure / (lateral_pressure + 1)
    
#     # Clinical classification
#     if results["max_pressure"] < 200:
#         results["risk_level"] = "Normal"
#         results["risk_color"] = "green"
#     elif results["max_pressure"] < 400:
#         results["risk_level"] = "Mild"
#         results["risk_color"] = "yellow"
#     elif results["max_pressure"] < 600:
#         results["risk_level"] = "Moderate"
#         results["risk_color"] = "orange"
#     elif results["max_pressure"] < 800:
#         results["risk_level"] = "High"
#         results["risk_color"] = "red"
#     else:
#         results["risk_level"] = "Very High"
#         results["risk_color"] = "darkred"
    
#     return results, foot_4x3

# # =============================================================================
# # VISUALIZATION FUNCTIONS
# # =============================================================================

# def plot_anatomical_foot_pressure(frame_idx=-1, save=False):
#     """Create anatomical foot pressure map"""
    
#     # Get frame data
#     if frame_idx == -1:
#         frame_idx = len(data) - 1
#     frame_data = data[frame_idx]
    
#     # Analyze
#     results, foot_4x3 = analyze_pressure(frame_data)
    
#     # Create figure
#     fig = plt.figure(figsize=(18, 10))
#     gs = GridSpec(2, 3, figure=fig, width_ratios=[1.2, 0.9, 0.9], height_ratios=[1, 1])
    
#     # ===== MAIN FOOT MAP (Left panel) =====
#     ax1 = fig.add_subplot(gs[:, 0])
    
#     # Create foot outline
#     foot_outline(ax1)
    
#     # Plot sensor positions with pressure values
#     for row in range(4):
#         for col in range(3):
#             sensor = ANATOMICAL_4X3[(row, col)]
#             value = foot_4x3[row, col]
            
#             # Calculate position in normalized coordinates
#             x = col * 0.33 + 0.17
#             y = 0.85 - row * 0.22  # 4 rows
            
#             # Determine color based on pressure
#             if value < 200:
#                 color = 'green'
#                 text_color = 'black'
#             elif value < 400:
#                 color = 'yellow'
#                 text_color = 'black'
#             elif value < 600:
#                 color = 'orange'
#                 text_color = 'white'
#             elif value < 800:
#                 color = 'red'
#                 text_color = 'white'
#             else:
#                 color = 'darkred'
#                 text_color = 'white'
            
#             # Draw sensor circle
#             circle = Circle((x, y), 0.08, color=color, alpha=0.7, ec='black', linewidth=1)
#             ax1.add_patch(circle)
            
#             # Add sensor abbreviation and value
#             ax1.text(x, y+0.03, sensor['abbr'], ha='center', va='bottom', 
#                     fontsize=9, fontweight='bold', color=text_color)
#             ax1.text(x, y-0.03, f"{value}", ha='center', va='top', 
#                     fontsize=8, color=text_color)
            
#             # Add sensor name
#             ax1.text(x, y-0.12, sensor['name'], ha='center', va='top', 
#                     fontsize=7, rotation=45, style='italic')
    
#     ax1.set_xlim(0, 1)
#     ax1.set_ylim(0, 1)
#     ax1.set_aspect('equal')
#     ax1.axis('off')
#     ax1.set_title('ANATOMICAL FOOT PRESSURE MAP', fontsize=14, fontweight='bold', pad=20)
    
#     # Add region labels
#     ax1.text(0.5, 0.95, 'TOES', ha='center', fontsize=12, fontweight='bold', 
#             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
#     ax1.text(0.5, 0.73, 'METATARSAL HEADS', ha='center', fontsize=12, fontweight='bold',
#             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
#     ax1.text(0.5, 0.51, 'MIDFOOT/ARCH', ha='center', fontsize=12, fontweight='bold',
#             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
#     ax1.text(0.5, 0.29, 'HEEL', ha='center', fontsize=12, fontweight='bold',
#             bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))
    
#     # ===== CLINICAL METRICS (Top right) =====
#     ax2 = fig.add_subplot(gs[0, 1])
#     ax2.axis('off')
#     ax2.set_title('🩺 CLINICAL METRICS', fontsize=14, fontweight='bold', color='navy')
    
#     metrics_text = [
#         f"Peak Pressure: {results['max_pressure']}",
#         f"Mean Pressure: {results['mean_pressure']:.1f}",
#         f"Total Load: {results['total_load']}",
#         f"Risk Level: {results['risk_level']}",
#         "",
#         "REGIONAL PRESSURES:",
#         f"  Forefoot: {results['forefoot_avg']:.1f}",
#         f"  Metatarsals: {results['metatarsal_avg']:.1f}",
#         f"  Midfoot: {results['midfoot_avg']:.1f}",
#         f"  Heel: {results['heel_avg']:.1f}"
#     ]
    
#     for i, text in enumerate(metrics_text):
#         if i == 3:  # Risk level line
#             ax2.text(0.1, 0.9 - i*0.07, text, fontsize=11, transform=ax2.transAxes,
#                     bbox=dict(boxstyle='round', facecolor=results['risk_color'], alpha=0.3))
#         else:
#             ax2.text(0.1, 0.9 - i*0.07, text, fontsize=10, transform=ax2.transAxes)
    
#     # ===== CLINICAL INDICATORS (Bottom right left) =====
#     ax3 = fig.add_subplot(gs[1, 1])
#     ax3.axis('off')
#     ax3.set_title('⚠️ CLINICAL INDICATORS', fontsize=14, fontweight='bold', color='darkred')
    
#     # Check for high pressure areas
#     warnings = []
#     if results['big_toe'] > 400:
#         warnings.append("⚠️ High pressure under big toe")
#     if results['first_met'] > 500:
#         warnings.append("⚠️ High pressure - 1st met head")
#     if results['medial_heel'] > 600:
#         warnings.append("⚠️ High pressure - medial heel")
#     if results['forefoot_heel_ratio'] > 1.5:
#         warnings.append("⚠️ Forefoot dominant gait")
#     elif results['forefoot_heel_ratio'] < 0.5:
#         warnings.append("⚠️ Heel dominant gait")
    
#     if not warnings:
#         warnings.append("No clinical warnings")
    
#     for i, warning in enumerate(warnings):
#         ax3.text(0.1, 0.8 - i*0.15, warning, fontsize=11, transform=ax3.transAxes,
#                 bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.5))
    
#     # ===== PRESSURE DISTRIBUTION (Right column) =====
#     ax4 = fig.add_subplot(gs[:, 2])
    
#     # Create bar chart of regional pressures
#     regions = ['Forefoot', 'Metatarsals', 'Midfoot', 'Heel']
#     values = [results['forefoot_avg'], results['metatarsal_avg'], 
#               results['midfoot_avg'], results['heel_avg']]
#     colors = ['blue', 'green', 'yellow', 'red']
    
#     bars = ax4.bar(regions, values, color=colors, alpha=0.7)
#     ax4.set_ylabel('Pressure', fontsize=12)
#     ax4.set_title('📊 PRESSURE DISTRIBUTION', fontsize=14, fontweight='bold')
#     ax4.grid(True, alpha=0.3, axis='y')
    
#     # Add value labels on bars
#     for bar, val in zip(bars, values):
#         height = bar.get_height()
#         ax4.text(bar.get_x() + bar.get_width()/2., height,
#                 f'{val:.0f}', ha='center', va='bottom', fontsize=10)
    
#     # Add medial-lateral balance inset
#     balance_ax = ax4.inset_axes([0.1, 0.6, 0.3, 0.3])
#     balance_ax.pie([results['medial_lateral_ratio'], 2-results['medial_lateral_ratio']], 
#                    colors=['blue', 'red'], labels=['Medial', 'Lateral'], 
#                    autopct='%1.0f%%', startangle=90, textprops={'fontsize':8})
#     balance_ax.set_title('M/L Balance', fontsize=9)
    
#     plt.suptitle(f'FOOT PRESSURE ANALYSIS - Frame {frame_idx}', fontsize=16, fontweight='bold', y=0.98)
#     plt.tight_layout()
    
#     if save:
#         plt.savefig(f'foot_analysis_frame_{frame_idx}.png', dpi=150, bbox_inches='tight')
    
#     plt.show()
    
#     # Print clinical report
#     print_clinical_report(results, frame_idx)

# def foot_outline(ax):
#     """Draw a foot outline"""
#     # Create a simple foot shape
#     foot_points = [
#         (0.2, 0.1), (0.8, 0.1),  # Heel
#         (0.9, 0.3), (0.9, 0.5), (0.85, 0.7),  # Lateral side
#         (0.7, 0.85), (0.5, 0.9), (0.3, 0.85),  # Toes
#         (0.15, 0.7), (0.1, 0.5), (0.1, 0.3), (0.2, 0.1)  # Medial side
#     ]
    
#     foot_poly = Polygon(foot_points, fill=False, edgecolor='black', linewidth=2)
#     ax.add_patch(foot_poly)

# def print_clinical_report(results, frame_idx):
#     """Print a clinical-style report"""
#     print("\n" + "="*70)
#     print("CLINICAL FOOT PRESSURE REPORT")
#     print("="*70)
#     print(f"Frame: {frame_idx}")
#     print(f"Risk Assessment: {results['risk_level']}")
#     print("-"*70)
#     print("REGIONAL ANALYSIS:")
#     print(f"  • Forefoot (Toes): {results['forefoot_avg']:.1f} (Peak: {results['forefoot_max']})")
#     print(f"  • Metatarsal Heads: {results['metatarsal_avg']:.1f} (Peak: {results['metatarsal_max']})")
#     print(f"  • Midfoot/Arch: {results['midfoot_avg']:.1f} (Peak: {results['midfoot_max']})")
#     print(f"  • Heel: {results['heel_avg']:.1f} (Peak: {results['heel_max']})")
#     print("-"*70)
#     print("CLINICAL INDICATORS:")
#     print(f"  • Big Toe Pressure: {results['big_toe']}")
#     print(f"  • 1st Metatarsal: {results['first_met']}")
#     print(f"  • Medial Heel: {results['medial_heel']}")
#     print(f"  • Lateral Heel: {results['lateral_heel']}")
#     print("-"*70)
#     print("GAIT ANALYSIS:")
#     if results['forefoot_heel_ratio'] > 1.3:
#         print("  • Forefoot Striker (anterior loading)")
#     elif results['forefoot_heel_ratio'] < 0.7:
#         print("  • Heel Striker (posterior loading)")
#     else:
#         print("  • Balanced Gait Pattern")
    
#     if results['medial_lateral_ratio'] > 1.2:
#         print("  • Medial Loading Pattern (Pronation)")
#     elif results['medial_lateral_ratio'] < 0.8:
#         print("  • Lateral Loading Pattern (Supination)")
#     else:
#         print("  • Balanced Medial-Lateral Distribution")
#     print("="*70)

# # =============================================================================
# # MAIN EXECUTION
# # =============================================================================

# if __name__ == "__main__":
    
#     print("\n" + "="*70)
#     print("PROFESSIONAL FOOT PRESSURE ASSESSMENT SYSTEM")
#     print("="*70)
    
#     print(f"\nAnalyzing {len(data)} frames of foot pressure data")
#     print(f"Anatomical grid: 4×3 (12 anatomical regions)")
#     print(f"Pressure range: {np.min(data)} - {np.max(data)}")
    
#     # Show most recent frame
#     plot_anatomical_foot_pressure(frame_idx=-1, save=True)
    
#     # Show summary statistics
#     print("\n" + "="*70)
#     print("SUMMARY STATISTICS (All Frames)")
#     print("="*70)
    
#     all_results = [analyze_pressure(frame)[0] for frame in data]
    
#     print(f"Average Peak Pressure: {np.mean([r['max_pressure'] for r in all_results]):.1f}")
#     print(f"Average Forefoot Pressure: {np.mean([r['forefoot_avg'] for r in all_results]):.1f}")
#     print(f"Average Metatarsal Pressure: {np.mean([r['metatarsal_avg'] for r in all_results]):.1f}")
#     print(f"Average Midfoot Pressure: {np.mean([r['midfoot_avg'] for r in all_results]):.1f}")
#     print(f"Average Heel Pressure: {np.mean([r['heel_avg'] for r in all_results]):.1f}")
    
#     # Risk level distribution
#     risk_levels = [r['risk_level'] for r in all_results]
#     print(f"\nRisk Distribution:")
#     for level in ['Normal', 'Mild', 'Moderate', 'High', 'Very High']:
#         count = risk_levels.count(level)
#         if count > 0:
#             print(f"  • {level}: {count} frames ({count/len(risk_levels)*100:.1f}%)")

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from matplotlib.path import Path
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

# SENSORS = {
#     # idx: (name, zone, x_norm, y_norm, clinical_note)
#     # x/y are normalized 0-1 positions on the foot outline (x=medial→lateral, y=toe→heel)
#      0: {"name": "Hallux Med",    "zone": "Big Toe",    "x": 0.30, "y": 0.94, "abbr": "BT₁"},
#      1: {"name": "Hallux Lat",   "zone": "Big Toe",    "x": 0.55, "y": 0.92, "abbr": "BT₂"},
#      2: {"name": "Toe 2",        "zone": "Toes",       "x": 0.55, "y": 0.85, "abbr": "T2"},
#      3: {"name": "Toe 3",        "zone": "Toes",       "x": 0.65, "y": 0.82, "abbr": "T3"},
#      4: {"name": "Toe 4",        "zone": "Toes",       "x": 0.72, "y": 0.78, "abbr": "T4"},
#      5: {"name": "Toe 5",        "zone": "Toes",       "x": 0.78, "y": 0.74, "abbr": "T5"},
#      6: {"name": "Met 1",        "zone": "Metatarsal", "x": 0.28, "y": 0.72, "abbr": "M1"},
#      7: {"name": "Met 2",        "zone": "Metatarsal", "x": 0.40, "y": 0.70, "abbr": "M2"},
#      8: {"name": "Met 3",        "zone": "Metatarsal", "x": 0.52, "y": 0.68, "abbr": "M3"},
#      9: {"name": "Met 4",        "zone": "Metatarsal", "x": 0.63, "y": 0.65, "abbr": "M4"},
#     10: {"name": "Met 5",        "zone": "Metatarsal", "x": 0.74, "y": 0.62, "abbr": "M5"},
#     11: {"name": "Arch Med",     "zone": "Midfoot",    "x": 0.22, "y": 0.50, "abbr": "AM"},
#     12: {"name": "Arch Cen",     "zone": "Midfoot",    "x": 0.42, "y": 0.48, "abbr": "AC"},
#     13: {"name": "Arch Lat",     "zone": "Midfoot",    "x": 0.62, "y": 0.46, "abbr": "AL"},
#     14: {"name": "Heel Med",     "zone": "Heel",       "x": 0.32, "y": 0.16, "abbr": "HM"},
#     15: {"name": "Heel Lat",     "zone": "Heel",       "x": 0.62, "y": 0.16, "abbr": "HL"},
# }

SENSORS = {

    # Big Toe
     0: {"name": "Hallux Med",  "zone": "Big Toe",    "x": 0.34, "y": 0.96, "abbr": "BT₁"},
     1: {"name": "Hallux Lat",  "zone": "Big Toe",    "x": 0.52, "y": 0.94, "abbr": "BT₂"},

    # Toes arc (better spacing)
     2: {"name": "Toe 2", "zone": "Toes", "x": 0.55, "y": 0.88, "abbr": "T2"},
     3: {"name": "Toe 3", "zone": "Toes", "x": 0.65, "y": 0.84, "abbr": "T3"},
     4: {"name": "Toe 4", "zone": "Toes", "x": 0.74, "y": 0.79, "abbr": "T4"},
     5: {"name": "Toe 5", "zone": "Toes", "x": 0.83, "y": 0.74, "abbr": "T5"},

    # Metatarsal arc (expanded laterally)
     6: {"name": "Met 1", "zone": "Metatarsal", "x": 0.32, "y": 0.74, "abbr": "M1"},
     7: {"name": "Met 2", "zone": "Metatarsal", "x": 0.44, "y": 0.71, "abbr": "M2"},
     8: {"name": "Met 3", "zone": "Metatarsal", "x": 0.57, "y": 0.68, "abbr": "M3"},
     9: {"name": "Met 4", "zone": "Metatarsal", "x": 0.69, "y": 0.65, "abbr": "M4"},
    10: {"name": "Met 5", "zone": "Metatarsal", "x": 0.80, "y": 0.61, "abbr": "M5"},

    # Arch
    11: {"name": "Arch Med", "zone": "Midfoot", "x": 0.26, "y": 0.52, "abbr": "AM"},
    12: {"name": "Arch Cen", "zone": "Midfoot", "x": 0.44, "y": 0.48, "abbr": "AC"},
    13: {"name": "Arch Lat", "zone": "Midfoot", "x": 0.62, "y": 0.46, "abbr": "AL"},

    # Heel (slightly widened)
    14: {"name": "Heel Med", "zone": "Heel", "x": 0.38, "y": 0.16, "abbr": "HM"},
    15: {"name": "Heel Lat", "zone": "Heel", "x": 0.66, "y": 0.16, "abbr": "HL"},
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
# FOOT OUTLINE SHAPE
# =============================================================================

# def draw_foot_outline(ax, alpha=0.12):
#     """Draw anatomically-shaped right foot outline."""
#     # Foot outline in normalized (x,y) coords, y=0 heel, y=1 toe
#     outline_x = [0.42, 0.38, 0.30, 0.22, 0.18, 0.18, 0.20, 0.22, 0.24, 0.26,
#                   0.30, 0.36, 0.42, 0.52, 0.62, 0.70, 0.78, 0.82, 0.82, 0.80,
#                   0.78, 0.76, 0.74, 0.72, 0.68, 0.62, 0.55, 0.48, 0.44, 0.42]
#     outline_y = [0.04, 0.08, 0.10, 0.12, 0.18, 0.30, 0.45, 0.55, 0.62, 0.68,
#                   0.72, 0.76, 0.80, 0.84, 0.82, 0.79, 0.74, 0.68, 0.55, 0.45,
#                   0.35, 0.25, 0.18, 0.12, 0.08, 0.06, 0.04, 0.04, 0.04, 0.04]

#     ax.fill(outline_x, outline_y, color='#e8d5b7', alpha=alpha, zorder=0)
#     ax.plot(outline_x, outline_y, color='#8B7355', linewidth=1.5, alpha=0.5, zorder=1)

#     # Toe bumps
#     toe_x = [0.30, 0.40, 0.50, 0.60, 0.69]
#     toe_y = [0.94, 0.90, 0.87, 0.84, 0.80]
#     toe_r = [0.07, 0.055, 0.05, 0.045, 0.04]
#     for tx, ty, tr in zip(toe_x, toe_y, toe_r):
#         toe_circle = plt.Circle((tx, ty), tr, color='#e8d5b7', alpha=alpha*2,
#                                  ec='#8B7355', linewidth=1, zorder=1)
#         ax.add_patch(toe_circle)


# def draw_foot_outline(ax, alpha=0.10):
#     """
#     Anatomically smooth right foot outline using Bezier curves.
#     Clinical-grade shape (no polygon edges).
#     """

#     verts = [
#         (0.50, 0.02),  # Heel bottom center

#         # Medial heel → arch
#         (0.38, 0.03), (0.30, 0.08), (0.24, 0.18),
#         (0.20, 0.30), (0.22, 0.48), (0.28, 0.62),

#         # Medial forefoot → hallux
#         (0.30, 0.75), (0.34, 0.86), (0.40, 0.95),
#         (0.46, 1.00),

#         # Toes crest
#         (0.56, 1.02), (0.68, 0.98), (0.78, 0.90),

#         # Lateral forefoot
#         (0.86, 0.80), (0.90, 0.65), (0.86, 0.50),

#         # Lateral arch
#         (0.82, 0.38), (0.76, 0.26), (0.68, 0.16),

#         # Return to heel
#         (0.62, 0.08), (0.56, 0.04), (0.50, 0.01)
#     ]

#     codes = [Path.MOVETO] + [Path.CURVE4] * (len(verts) - 1)

#     path = Path(verts, codes)
#     patch = patches.PathPatch(
#         path,
#         facecolor='#f3e3c3',
#         edgecolor='#d2b48c',
#         lw=1.5,
#         alpha=alpha,
#         zorder=0
#     )

#     ax.add_patch(patch)
#     return patch

def draw_foot_outline(ax, alpha=0.10):
    verts = [
        (0.50, 0.04),

        # LATERAL SIDE (right, going up)
        (0.58, 0.03), (0.66, 0.05), (0.72, 0.10),
        (0.78, 0.16), (0.82, 0.24), (0.80, 0.34),
        (0.79, 0.42), (0.80, 0.50), (0.80, 0.58),
        (0.80, 0.64), (0.82, 0.68), (0.82, 0.72),
        (0.82, 0.75), (0.80, 0.78), (0.78, 0.80),

        # TOE BASES (scalloped)
        (0.76, 0.81), (0.74, 0.80), (0.72, 0.80),
        (0.70, 0.80), (0.68, 0.79), (0.66, 0.79),
        (0.62, 0.79), (0.58, 0.79), (0.54, 0.80),
        (0.50, 0.81), (0.44, 0.83), (0.38, 0.85),
        (0.32, 0.87), (0.27, 0.87), (0.24, 0.84),

        # MEDIAL SIDE (left, going down)
        (0.22, 0.80), (0.21, 0.75), (0.22, 0.70),
        (0.22, 0.64), (0.22, 0.56), (0.22, 0.48),
        (0.20, 0.42), (0.20, 0.36), (0.22, 0.30),
        (0.24, 0.22), (0.26, 0.14), (0.32, 0.08),
        (0.38, 0.04), (0.44, 0.03), (0.50, 0.04),
    ]

    codes = [Path.MOVETO] + [Path.CURVE4] * (len(verts) - 1)
    path = Path(verts, codes)
    patch = patches.PathPatch(
        path, facecolor='#f3e3c3', edgecolor='#8B6914',
        lw=1.5, alpha=alpha, zorder=0
    )
    ax.add_patch(patch)

    # Individual toe ellipses — hallux largest, little toe smallest
    toes = [
        (0.31, 0.93, 0.075, 0.065),  # Hallux (big toe)
        (0.46, 0.91, 0.055, 0.050),  # Toe 2
        (0.58, 0.88, 0.048, 0.044),  # Toe 3
        (0.68, 0.85, 0.042, 0.038),  # Toe 4
        (0.77, 0.82, 0.036, 0.032),  # Toe 5 (little)
    ]
    for (cx, cy, rx, ry) in toes:
        ellipse = patches.Ellipse(
            (cx, cy), width=rx*2, height=ry*2,
            facecolor='#f3e3c3', edgecolor='#8B6914',
            lw=1.8, alpha=alpha, zorder=0
        )
        ax.add_patch(ellipse)

    return patch

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

    # draw_foot_outline(ax_foot)

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
    # Mask outside foot (rough ellipse mask)
    # foot_cx, foot_cy, foot_rx, foot_ry = 0.50, 0.50, 0.30, 0.48
    # mask = ((XX - foot_cx)**2 / foot_rx**2 + (YY - foot_cy)**2 / foot_ry**2) > 1
    # heatmap_norm[mask] = np.nan
    
    # Draw anatomical foot
    foot_patch = draw_foot_outline(ax_foot)
    
    im = ax_foot.imshow(
        heatmap_norm,
        origin='lower',
        extent=[0, 1, 0, 1],
        cmap=PRESSURE_CMAP,
        alpha=0.85,
       # alpha=0.75
        vmin=0,
        vmax=1,
        zorder=2,
        aspect='auto'
    )
    
    # Clip heatmap to foot shape
    im.set_clip_path(foot_patch)


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
   # ax_trend = fig.add_subplot(gs[2, 1])
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