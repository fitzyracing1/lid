# LiDAR 3D Mapping - Quick Reference Card

## 🚀 Quick Start Commands

```bash
# 1. Test your sensor
python test_sensor.py

# 2. Capture with live visualization (RECOMMENDED!)
python capture_and_visualize.py

# 3. View interactively in browser
python web_viewer.py output/lidar_map_*.npy --view all --auto-open
```

---

## 📋 All Available Scripts

| Script | Purpose | Output |
|--------|---------|--------|
| `test_sensor.py` | Test sensor connection | Single test scan |
| `capture_and_map.py` | Automated capture & mapping | Complete 3D map |
| `capture_and_visualize.py` | Capture with live view | Map + real-time viz |
| `web_viewer.py` | Interactive HTML viewer | Browser-based 3D viewer |
| `examples/basic_capture.py` | Learn sensor basics | Demo scan |
| `examples/processing_demo.py` | Learn processing | Processed demo |
| `examples/mapping_demo.py` | Learn mapping | Demo map |

---

## 🎛️ Web Viewer Options

```bash
# All views (recommended)
python web_viewer.py map.npy --view all --auto-open

# Single 3D view
python web_viewer.py map.npy --view single --auto-open

# Color options
python web_viewer.py map.npy --color-by distance  # or: z, height, uniform

# Point size
python web_viewer.py map.npy --point-size 3.0

# Density map with custom grid
python web_viewer.py map.npy --view density --grid-size 0.05
```

---

## 📁 File Structure

```
lid/
├── capture_and_map.py          # Main capture script
├── capture_and_visualize.py    # Capture with live view
├── web_viewer.py               # Interactive viewer
├── test_sensor.py              # Sensor test
├── config/
│   └── config.yaml             # Configuration
├── data/
│   ├── raw/                    # Raw sensor data
│   └── processed/              # Processed scans
└── output/
    ├── lidar_map_*.npy         # 3D maps
    ├── viewer*.html            # Web visualizations
    └── map_3d_view.png         # Static images
```

---

## ⚙️ Configuration Quick Edit

Edit `config/config.yaml`:

```yaml
# Sensor settings
sensor:
  port: /dev/ttyUSB0           # Change for your sensor
  baudrate: 115200

# Capture settings
mapping:
  num_scans: 4                 # Number of scans to capture

# Processing settings
processing:
  min_distance: 0.5            # Min range (meters)
  max_distance: 10.0           # Max range (meters)
  voxel_size: 0.05             # Downsampling size
```

---

## 🎯 Common Workflows

### Quick Scan (2 minutes)
```bash
python capture_and_visualize.py
python web_viewer.py output/lidar_map_*.npy --view all --auto-open
```

### High Quality (5 minutes)
```bash
# Edit config.yaml: num_scans: 8
python capture_and_visualize.py
python web_viewer.py output/lidar_map_*.npy --view all --point-size 1.5
```

### Test & Verify
```bash
python test_sensor.py
python examples/basic_capture.py
python examples/processing_demo.py
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| Sensor not found | Check port: `ls /dev/tty.*` and update config.yaml |
| Empty scans | Verify baudrate, check sensor power |
| Slow processing | Increase voxel_size in config.yaml |
| No 3D viewer | Use Python 3.8-3.12 for Open3D support |
| Import errors | `source venv/bin/activate` first |

---

## 💡 Tips

### Better Scans
- Ensure 30-50% overlap between positions
- Vary sensor height for 3D coverage
- Stay within sensor range (0.5-10m typically)

### Better Visualizations
- Dense clouds (>10k points): `--point-size 1.0`
- Sparse clouds (<1k points): `--point-size 4.0`
- Detailed analysis: `--grid-size 0.05`

### Faster Processing
```yaml
processing:
  voxel_size: 0.1              # Larger = faster
  outlier_removal:
    enabled: false             # Skip for speed
```

### Higher Quality
```yaml
processing:
  voxel_size: 0.01             # Smaller = more detail
  outlier_removal:
    enabled: true
    nb_neighbors: 30           # Better filtering
```

---

## 📊 Understanding Output

### Point Cloud Stats
- **Total points**: More = better coverage
- **X/Y/Z range**: Physical dimensions of scanned area
- **Centroid**: Center point of scan

### Web Viewer Views
- **3D View**: Rotate/zoom full point cloud
- **Multi-View**: 3D + top-down + side views
- **Density Map**: Bird's eye point density
- **Height Histogram**: Vertical distribution

---

## 🔗 Python API Quick Reference

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sensor.capture import LiDARSensor
from processing.pipeline import process_point_cloud, load_config
from mapping.mapper import merge_scans, save_map
from visualization.plotter import plot_3d_scatter

# Capture
sensor = LiDARSensor(port="/dev/ttyUSB0")
sensor.connect()
scan = sensor.capture_scan()
sensor.disconnect()

# Process
config = load_config()
processed = process_point_cloud(scan, config)

# Map
scans = [scan1, scan2, scan3]
map_3d = merge_scans(scans)
save_map(map_3d, "output/map.npy")

# Visualize
plot_3d_scatter(map_3d, title="My Map")
```

---

## 📚 Documentation

- **Full Guide**: See `USAGE_GUIDE.md`
- **README**: See `README.md`
- **Examples**: See `examples/README.md`
- **Config**: See `config/config.yaml`

---

## 🆘 Getting Help

1. Check `USAGE_GUIDE.md` for detailed workflows
2. Run examples to learn features
3. Check errors with `python test_sensor.py`
4. Verify environment: `source venv/bin/activate`

---

**Version**: 1.0  
**Python**: 3.8+ (3.8-3.12 for full Open3D support)  
**Updated**: December 2025
