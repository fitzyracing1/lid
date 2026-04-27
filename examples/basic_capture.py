"""
Example: Basic LiDAR scan capture and visualization
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
from sensor.capture import LiDARSensor
from visualization.plotter import plot_2d_scan, plot_3d_scatter


def main():
    """Capture and visualize a simple scan"""
    
    print("LiDAR Basic Capture Example")
    print("=" * 50)
    
    # Create sensor instance
    # Note: This example uses simulated data since hardware may not be connected
    print("\nSimulating LiDAR scan...")
    
    # Simulate a scan (in real use, connect to actual sensor)
    angles = np.linspace(0, 360, 360, endpoint=False)
    distances = 2.0 + 0.5 * np.sin(np.deg2rad(angles * 3))  # Simulated pattern
    
    # Add some noise
    distances += np.random.normal(0, 0.05, len(distances))
    
    # Convert to 3D points
    sensor = LiDARSensor()
    points = sensor.angles_distances_to_xyz(angles, distances, z_height=0.0)
    
    print(f"Generated {len(points)} points")
    
    # Visualize in 2D
    print("\nDisplaying 2D scan plot...")
    plot_2d_scan(angles, distances, title="Simulated LiDAR Scan")
    
    # Visualize in 3D
    print("\nDisplaying 3D scatter plot...")
    plot_3d_scatter(points, title="Simulated 3D Point Cloud")
    
    # Save data
    output_file = "data/raw/example_scan.npy"
    np.save(output_file, points)
    print(f"\nSaved scan data to {output_file}")


if __name__ == "__main__":
    main()
