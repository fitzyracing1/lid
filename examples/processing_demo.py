"""
Example: Process and filter point cloud data
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
from processing.filters import filter_distance_range
from visualization.plotter import plot_3d_scatter

try:
    from processing.filters import downsample_voxel, remove_outliers
    from visualization.viewer import view_point_cloud
    OPEN3D_AVAILABLE = True
except ImportError:
    OPEN3D_AVAILABLE = False
    print("Warning: Some features require open3d. Install with: pip install open3d")


def main():
    """Demonstrate point cloud processing pipeline"""
    
    print("Point Cloud Processing Example")
    print("=" * 50)
    
    # Generate sample point cloud (normally loaded from file)
    print("\nGenerating sample point cloud...")
    n_points = 10000
    
    # Create a sphere with noise
    theta = np.random.uniform(0, 2*np.pi, n_points)
    phi = np.random.uniform(0, np.pi, n_points)
    r = 2.0 + np.random.normal(0, 0.1, n_points)
    
    x = r * np.sin(phi) * np.cos(theta)
    y = r * np.sin(phi) * np.sin(theta)
    z = r * np.cos(phi)
    
    points = np.column_stack([x, y, z])
    
    # Add some outliers
    outliers = np.random.uniform(-5, 5, (100, 3))
    points = np.vstack([points, outliers])
    
    print(f"Created {len(points)} points (including outliers)")
    
    # Step 1: Distance filtering
    print("\nStep 1: Filtering by distance...")
    filtered = filter_distance_range(points, min_distance=0.5, max_distance=10.0)
    print(f"  Points after filtering: {len(filtered)}")
    
    if OPEN3D_AVAILABLE:
        # Step 2: Downsampling
        print("\nStep 2: Downsampling with voxel grid...")
        downsampled = downsample_voxel(filtered, voxel_size=0.1)
        print(f"  Points after downsampling: {len(downsampled)}")
        
        # Step 3: Outlier removal
        print("\nStep 3: Removing outliers...")
        clean = remove_outliers(downsampled, nb_neighbors=20, std_ratio=2.0)
        print(f"  Points after outlier removal: {len(clean)}")
        
        # Visualize results
        print("\nVisualizing processed point cloud...")
        view_point_cloud(clean, window_name="Processed Point Cloud")
    else:
        clean = filtered
        print("\nSkipping downsampling and outlier removal (open3d not available)")
        print("Visualizing with matplotlib...")
        plot_3d_scatter(clean, title="Processed Point Cloud")
    
    # Save processed data
    output_file = "data/processed/example_processed.npy"
    np.save(output_file, clean)
    print(f"\nSaved processed data to {output_file}")


if __name__ == "__main__":
    main()
