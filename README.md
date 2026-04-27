# LiDAR 3D Mapping System

A comprehensive Python-based system for processing LiDAR sensor data to create 3D maps and point cloud visualizations.

## Features

- **Sensor Interface**: Connect to and capture data from LiDAR close-range sensors
- **Point Cloud Processing**: Filter, downsample, and clean point cloud data
- **3D Mapping**: Merge multiple scans into comprehensive 3D maps
- **Visualization**: Interactive 3D viewers and 2D plotting tools
- **Surface Reconstruction**: Generate mesh surfaces from point clouds
- **Flexible Pipeline**: Configurable processing parameters via YAML

## Project Structure

```
lid/
├── src/                      # Source code
│   ├── sensor/              # LiDAR sensor interface
│   │   ├── capture.py       # Data acquisition
│   │   └── calibration.py   # Sensor calibration
│   ├── processing/          # Point cloud processing
│   │   ├── filters.py       # Filtering operations
│   │   ├── registration.py  # Point cloud alignment
│   │   └── pipeline.py      # Processing pipeline
│   ├── visualization/       # Visualization tools
│   │   ├── viewer.py        # 3D viewer
│   │   └── plotter.py       # 2D plotting
│   ├── mapping/            # 3D mapping
│   │   ├── mapper.py        # Map creation
│   │   └── reconstruction.py # Surface reconstruction
│   └── main.py             # Main application
├── examples/               # Example scripts
├── tests/                  # Unit tests
├── data/                   # Data storage
│   ├── raw/               # Raw sensor data
│   └── processed/         # Processed data
├── output/                # Output maps and visualizations
├── config/                # Configuration files
│   └── config.yaml        # Main configuration
├── requirements.txt       # Python dependencies
└── setup.py              # Package setup

```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- **Note**: Full functionality requires Python 3.8-3.12 for Open3D support. Python 3.13+ users can install other dependencies but Open3D visualization features will be limited.

### Setup

1. **Clone or navigate to the repository**:
   ```bash
   cd /Users/joshuafitzgerald/lid
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   
   # If using Python 3.8-3.12, also install Open3D:
   pip install -r requirements-open3d.txt
   ```

4. **Install package in development mode**:
   ```bash
   pip install -e .
   ```

### Python 3.13 Users

Open3D does not yet support Python 3.13. You have two options:

**Option 1**: Use Python 3.12 (recommended for full functionality)
```bash
# Install Python 3.12 using pyenv or download from python.org
pyenv install 3.12.0
pyenv local 3.12.0
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-open3d.txt
```

**Option 2**: Use Python 3.13 without Open3D visualization
- Most processing and data capture features will work
- 3D visualization features using Open3D will not be available
- 2D plotting with matplotlib will still work

## Configuration

Edit `config/config.yaml` to customize:

- **Sensor settings**: Port, baudrate, scan parameters
- **Processing parameters**: Voxel size, outlier removal, filtering
- **Mapping settings**: Resolution, map size
- **Visualization**: Display options, colors, window size

## Usage

### Quick Start with Your LiDAR Sensor

**Step 1: Test your sensor connection**
```bash
python test_sensor.py
```
This will verify your LiDAR sensor is connected and working properly.

**Step 2: Capture and create a 3D map**
```bash
# Basic capture and mapping
python capture_and_map.py

# OR: Capture with real-time visualization (recommended!)
python capture_and_visualize.py
```
This will:
- Capture 4 scans from your LiDAR sensor
- Prompt you to move the sensor between scans
- Process all scans automatically
- Create a merged 3D map
- Save all data and visualizations
- (capture_and_visualize.py shows live updates as you scan!)

**Step 3: View your 3D map interactively**
```bash
# Create interactive web-based viewer
python web_viewer.py output/lidar_map_XXXXXX.npy --view all --auto-open
```
This creates interactive HTML visualizations you can explore in your browser:
- 3D view with rotation, zoom, and pan
- Multi-view layout (3D + top-down + side views)
- Density heatmap
- Height distribution histogram

### Main Application

The main application provides a command-line interface for common tasks:

```bash
# Capture a scan from LiDAR sensor
python src/main.py capture --output data/raw/scan1.npy

# Process a point cloud
python src/main.py process data/raw/scan1.npy --output data/processed/scan1.npy

# Visualize a point cloud
python src/main.py view data/processed/scan1.npy

# Create 3D map from multiple scans
python src/main.py map data/processed/*.npy --output output/map.ply
```

### Example Scripts

Run the example scripts to learn the workflow:

```bash
# Basic capture and visualization
python examples/basic_capture.py

# Point cloud processing demonstration
python examples/processing_demo.py

# 3D mapping from multiple scans
python examples/mapping_demo.py
```

### Python API

Use the library in your own Python scripts:

```python
import numpy as np
from sensor.capture import LiDARSensor
from processing.pipeline import process_point_cloud
from visualization.viewer import view_point_cloud
from mapping.mapper import create_3d_map

# Capture scan
sensor = LiDARSensor(port="/dev/ttyUSB0")
sensor.connect()
angles, distances = sensor.capture_scan()
points = sensor.angles_distances_to_xyz(angles, distances)
sensor.disconnect()

# Process point cloud
processed = process_point_cloud(points)

# Visualize
view_point_cloud(processed)

# Create map from multiple scans
scans = [scan1, scan2, scan3]
map_3d = create_3d_map(scans, output_path="output/my_map.ply")
```

## Hardware Setup

### Supported Sensors

This system is designed for close-range LiDAR sensors with serial/UART interface. Examples include:

- Benewake TF series (TFmini, TF02, TF03)
- RPLIDAR A1/A2
- YDLIDAR X2/X4
- Custom LiDAR sensors with serial output

### Connection

1. Connect LiDAR sensor to computer via USB-to-Serial adapter
2. Identify serial port:
   ```bash
   # macOS/Linux
   ls /dev/tty.*
   
   # Common ports: /dev/ttyUSB0, /dev/tty.usbserial-*
   ```

3. Update `config/config.yaml` with correct port

4. Ensure proper permissions:
   ```bash
   # Linux
   sudo usermod -a -G dialout $USER
   # Log out and back in
   ```

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_sensor.py
```

## Workflow Examples

### Automated Mapping (Recommended)

Use the automated script for easiest operation:

```bash
# Run complete mapping workflow
python capture_and_map.py
```

The script will guide you through:
1. Connecting to sensor
2. Capturing multiple scans (moves between scans)
3. Processing all data
4. Creating 3D map
5. Generating visualizations

### Manual Workflow

For more control, use individual commands:

```bash
# 1. Test sensor first
python test_sensor.py

# 2. Capture multiple scans from different positions
python src/main.py capture --output data/raw/scan1.npy
# Move sensor to new position
python src/main.py capture --output data/raw/scan2.npy
# Move sensor to new position
python src/main.py capture --output data/raw/scan3.npy

# 3. Process each scan
python src/main.py process data/raw/scan1.npy --output data/processed/scan1.npy
python src/main.py process data/raw/scan2.npy --output data/processed/scan2.npy
python src/main.py process data/raw/scan3.npy --output data/processed/scan3.npy

# 4. Create 3D map
python src/main.py map data/processed/*.npy --output output/final_map.npy

# 5. View the result (requires matplotlib)
python -c "import numpy as np; from visualization.plotter import plot_3d_scatter; plot_3d_scatter(np.load('output/final_map.npy'))"
```

## Advanced Features

### Point Cloud Registration

Align multiple scans using ICP (Iterative Closest Point):

```python
from processing.registration import register_point_clouds

registered = register_point_clouds([scan1, scan2, scan3], threshold=0.02)
```

### Surface Reconstruction

Generate mesh from point cloud:

```python
from mapping.reconstruction import build_mesh, save_mesh

mesh, densities = build_mesh(points, depth=9, method="poisson")
save_mesh(mesh, "output/surface.ply")
```

### Batch Processing

Process multiple files at once:

```python
from processing.pipeline import batch_process

batch_process(
    input_dir="data/raw",
    output_dir="data/processed",
    config_path="config/config.yaml"
)
```

## Troubleshooting

### Sensor Connection Issues

- Check serial port name: `ls /dev/tty.*`
- Verify baudrate matches sensor specification
- Check cable connections and power supply
- Test with serial monitor first

### Visualization Issues

- Update graphics drivers
- Try software rendering: `export LIBGL_ALWAYS_SOFTWARE=1`
- Reduce point cloud size for better performance

### Processing Errors

- Check point cloud has sufficient points (>100)
- Adjust filtering parameters in config.yaml
- Verify input file format (should be Nx3 numpy array)

## Dependencies

Major libraries used:

- **numpy**: Numerical computing
- **open3d**: 3D point cloud processing and visualization
- **matplotlib**: 2D plotting
- **scipy**: Scientific computing
- **pyserial**: Serial communication with sensors
- **pyyaml**: Configuration file parsing

See `requirements.txt` for complete list.

## Performance Tips

- Use voxel downsampling to reduce point count
- Process scans in parallel for large datasets
- Save intermediate results to avoid reprocessing
- Use appropriate voxel size (larger = faster but less detail)

## Contributing

Contributions are welcome! Areas for improvement:

- Support for additional LiDAR sensor models
- Real-time visualization during capture
- SLAM (Simultaneous Localization and Mapping)
- Color information from RGB cameras
- Export to additional formats (LAS, E57)

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Open3D library for point cloud processing
- LiDAR sensor manufacturers for documentation
- Point cloud processing community

## Contact

For questions or support, please open an issue on GitHub.

---

**Happy Mapping! 🗺️**
