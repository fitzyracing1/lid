"""
3D point cloud viewer
"""

import numpy as np
import yaml
from pathlib import Path
from typing import Optional, List

try:
    import open3d as o3d
    OPEN3D_AVAILABLE = True
except ImportError:
    OPEN3D_AVAILABLE = False


def load_config(config_path: str = "config/config.yaml") -> dict:
    """Load visualization configuration"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def view_point_cloud(points: np.ndarray, 
                    colors: Optional[np.ndarray] = None,
                    config: Optional[dict] = None,
                    window_name: str = "LiDAR Point Cloud"):
    """
    Visualize point cloud in 3D viewer
    
    Args:
        points: Nx3 numpy array of points
        colors: Optional Nx3 numpy array of RGB colors (0-1 range)
        config: Optional configuration dictionary
        window_name: Window title
    """
    if not OPEN3D_AVAILABLE:
        print("Warning: open3d not available. Cannot display 3D visualization.")
        print("Install open3d with: pip install open3d")
        print("Alternatively, use matplotlib for 2D visualization.")
        return
    
    if config is None:
        config = load_config()
    
    viz_config = config.get('visualization', {})
    
    # Create point cloud object
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    
    if colors is not None:
        pcd.colors = o3d.utility.Vector3dVector(colors)
    else:
        # Color by height (z-coordinate)
        z_values = points[:, 2]
        z_norm = (z_values - z_values.min()) / (z_values.max() - z_values.min() + 1e-8)
        colors = np.zeros((len(points), 3))
        colors[:, 0] = z_norm  # Red channel
        colors[:, 2] = 1 - z_norm  # Blue channel
        pcd.colors = o3d.utility.Vector3dVector(colors)
    
    # Estimate normals for better visualization
    pcd.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamKNN(knn=30)
    )
    
    # Create coordinate frame
    coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(
        size=1.0, origin=[0, 0, 0]
    )
    
    # Visualization options
    vis = o3d.visualization.Visualizer()
    vis.create_window(
        window_name=window_name,
        width=viz_config.get('window_width', 1280),
        height=viz_config.get('window_height', 720)
    )
    
    vis.add_geometry(pcd)
    if viz_config.get('show_axes', True):
        vis.add_geometry(coordinate_frame)
    
    # Set rendering options
    render_opt = vis.get_render_option()
    render_opt.point_size = viz_config.get('point_size', 2.0)
    bg_color = viz_config.get('background_color', [0, 0, 0])
    render_opt.background_color = np.array(bg_color)
def view_multiple_clouds(point_clouds: List[np.ndarray],
                        colors: Optional[List[np.ndarray]] = None,
                        window_name: str = "Multiple Point Clouds"):
    """
    Visualize multiple point clouds together
    
    Args:
        point_clouds: List of Nx3 numpy arrays
        colors: Optional list of Nx3 color arrays
        window_name: Window title
    """
    if not OPEN3D_AVAILABLE:
        print("Warning: open3d not available. Cannot display 3D visualization.")
        print("Install open3d with: pip install open3d")
        return
    
    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name=window_name, width=1280, height=720)
    
    # Default colors for different clouds
    default_colors = [
        [1, 0, 0],  # Red
        [0, 1, 0],  # Green
        [0, 0, 1],  # Blue
        [1, 1, 0],  # Yellow
        [1, 0, 1],  # Magenta
        [0, 1, 1],  # Cyan
    ]
    
    for i, points in enumerate(point_clouds):
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        
        if colors and i < len(colors):
            pcd.colors = o3d.utility.Vector3dVector(colors[i])
        else:
            # Use default color
            color = default_colors[i % len(default_colors)]
            pcd.paint_uniform_color(color)
        
        vis.add_geometry(pcd)
    
    # Add coordinate frame
    coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(
        size=1.0, origin=[0, 0, 0]
    )
    vis.add_geometry(coordinate_frame)
def save_visualization(points: np.ndarray, 
                      output_path: str,
                      colors: Optional[np.ndarray] = None):
    """
    Save point cloud to file
    
    Args:
        points: Nx3 numpy array
        output_path: Output file path (.ply, .pcd, or .xyz)
        colors: Optional Nx3 color array
    """
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    if OPEN3D_AVAILABLE:
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        
        if colors is not None:
            pcd.colors = o3d.utility.Vector3dVector(colors)
        
        # Save file
        o3d.io.write_point_cloud(output_path, pcd)
        print(f"Point cloud saved to {output_path}")
    else:
        # Fallback to numpy
        np_path = output_path.replace('.ply', '.npy').replace('.pcd', '.npy')
        np.save(np_path, points)
        print(f"Point cloud saved to {np_path} (open3d not available)")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Save file
    o3d.io.write_point_cloud(output_path, pcd)
    print(f"Point cloud saved to {output_path}")


def main():
    """Main entry point for viewer"""
    import argparse
    parser = argparse.ArgumentParser(description='View LiDAR point cloud')
    parser.add_argument('input', help='Input point cloud file (.npy, .ply, or .pcd)')
    parser.add_argument('--config', default='config/config.yaml', help='Config file path')
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    # Load point cloud
    if input_path.suffix == '.npy':
        points = np.load(input_path)
    elif OPEN3D_AVAILABLE:
        pcd = o3d.io.read_point_cloud(str(input_path))
        points = np.asarray(pcd.points)
    else:
        print("Error: open3d required to load point cloud files other than .npy")
        print("Install with: pip install open3d")
        return
    
    print(f"Loaded {len(points)} points from {input_path}")
    
    # Visualize
    view_point_cloud(points, config=load_config(args.config))


if __name__ == "__main__":
    main()
