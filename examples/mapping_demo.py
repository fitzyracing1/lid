"""
Example: Create 3D map from multiple scans
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
from mapping.mapper import create_3d_map, save_map
from visualization.plotter import plot_3d_scatter

try:
    from visualization.viewer import view_point_cloud, view_multiple_clouds
    OPEN3D_AVAILABLE = True
except ImportError:
    OPEN3D_AVAILABLE = False
    print("Warning: open3d not available. Using matplotlib for visualization.")


def generate_sample_scan(center, rotation_angle=0, n_points=500):
    """Generate a sample scan around a center point"""
    
    # Generate points in a fan pattern
    angles = np.linspace(-np.pi/2, np.pi/2, n_points)
    distances = np.random.uniform(1.0, 3.0, n_points)
    
    # Convert to Cartesian
    x = distances * np.cos(angles)
    y = distances * np.sin(angles)
    z = np.zeros_like(x)
    
    points = np.column_stack([x, y, z])
    
    # Apply rotation
    cos_a = np.cos(rotation_angle)
    sin_a = np.sin(rotation_angle)
    rotation = np.array([
        [cos_a, -sin_a, 0],
        [sin_a, cos_a, 0],
        [0, 0, 1]
    ])
    
    points = points @ rotation.T
    
    # Translate to center
    points += center
    
    return points


def main():
    """Create 3D map from multiple scan positions"""
    
    print("3D Mapping Example")
    print("=" * 50)
    
    # Simulate multiple scans from different positions
    print("\nGenerating sample scans from different viewpoints...")
    
    scan_positions = [
        ([0, 0, 0], 0),           # Center, facing forward
        ([2, 0, 0], np.pi),       # Right side, facing back
        ([0, 2, 0], -np.pi/2),    # Front, facing right
        ([-2, 0, 0], 0),          # Left side, facing forward
    ]
    
    scans = []
    for i, (pos, angle) in enumerate(scan_positions, 1):
        print(f"  Scan {i} from position {pos}")
        scan = generate_sample_scan(pos, angle, n_points=500)
        scans.append(scan)
    
    # Visualize individual scans
    print("\nVisualizing individual scans...")
    if OPEN3D_AVAILABLE:
        view_multiple_clouds(scans, window_name="Multiple Scans (Before Mapping)")
    else:
        # Show first scan with matplotlib
        plot_3d_scatter(scans[0], title="First Scan (Multiple Scans Available)")
    
    # Create merged 3D map
    print("\nCreating 3D map...")
    map_points = create_3d_map(
        scans,
        output_path="output/example_map.ply",
        resolution=0.05
    )
    
    # Visualize final map
    print("\nVisualizing 3D map...")
    if OPEN3D_AVAILABLE:
        view_point_cloud(map_points, window_name="3D Map")
    else:
        plot_3d_scatter(map_points, title="3D Map")
    
    print(f"\nMap creation complete!")
    print(f"  Total scans: {len(scans)}")
    print(f"  Map points: {len(map_points)}")
    print(f"  Saved to: output/example_map.ply")


if __name__ == "__main__":
    main()
