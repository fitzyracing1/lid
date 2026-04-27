# LiDAR 3D Mapping - Complete Usage Guide

This guide covers all the tools and scripts available in the LiDAR 3D Mapping system.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Core Scripts](#core-scripts)
3. [Example Scripts](#example-scripts)
4. [Command-Line Options](#command-line-options)
5. [Workflows](#workflows)
6. [Tips and Tricks](#tips-and-tricks)

## Quick Start

### Fastest Way to Get Started

1. **Verify your sensor**:
   ```bash
   python test_sensor.py
   ```

2. **Capture with live visualization**:
   ```bash
   python capture_and_visualize.py
   ```

3. **Create interactive web viewer**:
   ```bash
   python web_viewer.py output/lidar_map_*.npy --view all --auto-open
   ```

## Core Scripts

### 1. `test_sensor.py` - Sensor Connection Test

**Purpose**: Verify your LiDAR sensor is connected and working

**Usage**:
```bash
python test_sensor.py
```

**What it does**:
- Attempts to connect to sensor on configured port
- Captures a single test scan
- Displays basic statistics
- Shows 2D visualization

**Output**:
- Console feedback on connection status
- Test scan saved to `data/raw/test_scan.npy`
- 2D plot displayed

---

### 2. `capture_and_map.py` - Automated Capture & Mapping

**Purpose**: Complete workflow for capturing multiple scans and creating a 3D map

**Usage**:
```bash
python capture_and_map.py
```

**What it does**:
1. Connects to sensor (or uses simulation if unavailable)
2. Captures 4 scans (configurable in `config/config.yaml`)
3. Pauses between scans for you to reposition sensor
4. Processes each scan (filtering, downsampling)
5. Merges all scans into a 3D map
6. Saves all data and visualizations

**Output**:
- Raw scans: `data/raw/scan_*.npy`
- Processed scans: `data/processed/scan_*.npy`
- Final map: `output/lidar_map_*.npy`
- Visualization: `output/map_3d_view.png`

**Best for**: Automated data collection without real-time feedback

---

### 3. `capture_and_visualize.py` - Real-Time Capture with Live View

**Purpose**: Capture scans with real-time visualization updates

**Usage**:
```bash
python capture_and_visualize.py
```

**What it does**:
- Same as `capture_and_map.py` but with live visualization
- Shows each scan immediately after capture in 3 views:
  - 3D view of current scan
  - Top-down view of current scan
  - Merged map of all scans so far
- Updates in real-time as you capture

**Output**: Same as `capture_and_map.py`

**Best for**: Interactive data collection where you want immediate feedback on sensor positioning

---

### 4. `web_viewer.py` - Interactive Web-Based 3D Viewer

**Purpose**: Create interactive HTML visualizations of point cloud data

**Usage**:
```bash
# Create all views (recommended)
python web_viewer.py <input.npy> --view all --auto-open

# Single 3D view only
python web_viewer.py <input.npy> --view single --auto-open

# Multi-view layout
python web_viewer.py <input.npy> --view multi --auto-open

# Density heatmap
python web_viewer.py <input.npy> --view density --auto-open

# Height histogram
python web_viewer.py <input.npy> --view height --auto-open
```

**Options**:
- `--view`: Type of visualization (single, multi, density, height, all)
- `--output`: Output HTML file path (default: `output/viewer.html`)
- `--color-by`: How to color points (z, distance, height, uniform)
- `--point-size`: Size of points in 3D view (default: 2.0)
- `--grid-size`: Grid cell size for density map in meters (default: 0.1)
- `--auto-open`: Automatically open in browser

**What it creates** (when using `--view all`):
- `viewer.html` - Index page with links to all views
- `viewer_3d.html` - Interactive 3D view (rotate, zoom, pan)
- `viewer_multi.html` - Multiple views side-by-side
- `viewer_density.html` - 2D density heatmap
- `viewer_height.html` - Height distribution histogram

**Best for**: 
- Detailed analysis of captured data
- Sharing visualizations (just send the HTML files)
- Presentations and reports

---

## Example Scripts

Located in the `examples/` directory. These demonstrate individual features.

### 1. `basic_capture.py`

**Purpose**: Learn how to capture a single scan

**Usage**:
```bash
python examples/basic_capture.py
```

**Demonstrates**:
- Connecting to sensor
- Capturing a scan
- Basic visualization

---

### 2. `processing_demo.py`

**Purpose**: Learn point cloud processing techniques

**Usage**:
```bash
python examples/processing_demo.py
```

**Demonstrates**:
- Distance filtering
- Voxel downsampling
- Outlier removal
- Visualization of each step

---

### 3. `mapping_demo.py`

**Purpose**: Learn how to create 3D maps from multiple scans

**Usage**:
```bash
python examples/mapping_demo.py
```

**Demonstrates**:
- Merging multiple scans
- Map creation
- Saving maps in different formats

---

## Command-Line Options

### Main Application (`src/main.py`)

```bash
# Capture mode
python src/main.py capture --output data/raw/scan1.npy

# Process mode
python src/main.py process input.npy --output processed.npy

# View mode
python src/main.py view input.npy --config config/config.yaml

# Map mode
python src/main.py map scan1.npy scan2.npy scan3.npy --output map.npy
```

---

## Workflows

### Workflow 1: Quick Scan and View

For quick data collection and viewing:

```bash
# 1. Capture with live view
python capture_and_visualize.py

# 2. View interactively
python web_viewer.py output/lidar_map_*.npy --view all --auto-open
```

**Time**: ~2-3 minutes for 4 scans

---

### Workflow 2: High-Quality Mapping

For detailed mapping projects:

```bash
# 1. Test sensor first
python test_sensor.py

# 2. Adjust config for more scans
# Edit config/config.yaml: num_scans: 8

# 3. Capture with real-time feedback
python capture_and_visualize.py

# 4. Create comprehensive visualizations
python web_viewer.py output/lidar_map_*.npy --view all --point-size 1.5 --grid-size 0.05

# 5. Analyze in browser
# Open output/viewer.html
```

**Time**: ~5-10 minutes for 8 scans

---

### Workflow 3: Batch Processing

For processing multiple datasets:

```bash
# Process all raw scans
for file in data/raw/*.npy; do
    python src/main.py process "$file" --output "data/processed/$(basename $file)"
done

# Create web viewers for all maps
for file in output/lidar_map_*.npy; do
    python web_viewer.py "$file" --view all --output "output/viewer_$(basename $file .npy).html"
done
```

---

### Workflow 4: Custom Python Script

For integration into your own projects:

```python
#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import numpy as np
from sensor.capture import LiDARSensor, create_simulated_scan
from processing.pipeline import process_point_cloud, load_config
from mapping.mapper import merge_scans, save_map
from visualization.plotter import plot_3d_scatter

# Load config
config = load_config()

# Connect to sensor
sensor = LiDARSensor(
    port=config['sensor']['port'],
    baudrate=config['sensor']['baudrate']
)

if sensor.connect():
    # Capture multiple scans
    scans = []
    for i in range(5):
        print(f"Capturing scan {i+1}/5...")
        scan = sensor.capture_scan()
        processed = process_point_cloud(scan, config)
        scans.append(processed)
        input("Move sensor and press Enter...")
    
    sensor.disconnect()
    
    # Create map
    final_map = merge_scans(scans)
    
    # Save
    save_map(final_map, "output/my_custom_map.npy")
    
    # Visualize
    plot_3d_scatter(final_map, title="My Custom Map")
else:
    print("Sensor not connected")
```

---

## Tips and Tricks

### 1. Sensor Positioning

For best results when capturing multiple scans:

- **Overlap**: Ensure 30-50% overlap between scans
- **Height variation**: Vary the sensor height for better 3D coverage
- **Rotation**: Rotate the sensor to cover different angles
- **Distance**: Keep objects within the sensor's optimal range (usually 0.5-10m)

### 2. Configuration Tuning

Edit `config/config.yaml` for different scenarios:

**For indoor rooms**:
```yaml
processing:
  min_distance: 0.2
  max_distance: 5.0
  voxel_size: 0.02
```

**For outdoor areas**:
```yaml
processing:
  min_distance: 1.0
  max_distance: 20.0
  voxel_size: 0.1
```

**For detailed objects**:
```yaml
processing:
  min_distance: 0.1
  max_distance: 2.0
  voxel_size: 0.005
```

### 3. Visualization Tips

**For dense point clouds** (>10,000 points):
```bash
# Use smaller point size
python web_viewer.py map.npy --point-size 1.0 --view single
```

**For sparse point clouds** (<1,000 points):
```bash
# Use larger point size
python web_viewer.py map.npy --point-size 4.0 --view single
```

**For analyzing specific areas**:
```bash
# Finer density grid
python web_viewer.py map.npy --view density --grid-size 0.05
```

### 4. Data Management

Organize your data by project:

```bash
# Create project-specific directories
mkdir -p data/raw/room1 data/processed/room1 output/room1

# Capture into project directory
# Edit capture scripts to save to project paths
```

### 5. Error Recovery

**If sensor disconnects during capture**:
- Already-captured scans are saved in `data/raw/`
- Process them manually with `src/main.py process`
- Create map from processed scans with `src/main.py map`

**If visualization crashes**:
- Data is still saved in `data/` directories
- Re-run visualization tools on saved data

### 6. Performance Optimization

**For faster processing** (less accurate):
```yaml
processing:
  voxel_size: 0.1  # Larger = faster
  outlier_removal:
    enabled: false  # Skip outlier removal
```

**For higher quality** (slower):
```yaml
processing:
  voxel_size: 0.01  # Smaller = more detail
  outlier_removal:
    enabled: true
    nb_neighbors: 30  # More neighbors = better filtering
```

---

## Troubleshooting

### Sensor Not Found
```bash
# List available serial ports
ls /dev/tty.*  # macOS/Linux
# or
ls /dev/ttyUSB*  # Linux

# Update config.yaml with correct port
```

### Slow Processing
```bash
# Increase voxel size in config.yaml
# Disable outlier removal for faster processing
```

### Empty Scans
```bash
# Check sensor is powered and connected
# Verify baudrate matches sensor specs
# Test with test_sensor.py first
```

### Visualization Issues
```bash
# Install plotly if using web viewer
pip install plotly

# For 3D Open3D viewer, use Python 3.8-3.12
```

---

## Next Steps

1. **Experiment with different sensor positions** to understand data collection
2. **Try different processing parameters** to optimize for your use case
3. **Integrate into your own projects** using the Python API
4. **Share your visualizations** - the HTML files are self-contained

For more information, see the main README.md file.
