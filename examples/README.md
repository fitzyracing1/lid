# Examples Directory

This directory contains example scripts demonstrating various features of the LiDAR 3D Mapping System.

## Available Examples

### 1. basic_capture.py
Demonstrates basic LiDAR scan capture and 2D/3D visualization.

```bash
python examples/basic_capture.py
```

### 2. processing_demo.py
Shows the complete point cloud processing pipeline including filtering, downsampling, and outlier removal.

```bash
python examples/processing_demo.py
```

### 3. mapping_demo.py
Demonstrates creating a 3D map by merging multiple scans from different viewpoints.

```bash
python examples/mapping_demo.py
```

## Note

The examples use simulated data for demonstration purposes. When connected to real hardware, replace the simulation code with actual sensor calls.
