"""
3D map creation from point clouds
"""

import numpy as np
from typing import List, Tuple, Optional
from pathlib import Path

try:
    import open3d as o3d
    OPEN3D_AVAILABLE = True
except ImportError:
    OPEN3D_AVAILABLE = False


def merge_scans(point_clouds: List[np.ndarray],
               remove_duplicates: bool = True,
               voxel_size: float = 0.01) -> np.ndarray:
    """
    Merge multiple point cloud scans into single map
    
    Args:
        point_clouds: List of Nx3 numpy arrays
        remove_duplicates: Whether to remove duplicate points
        voxel_size: Voxel size for deduplication
        
    Returns:
        Merged Nx3 numpy array
    """
    if len(point_clouds) == 0:
        raise ValueError("point_clouds list cannot be empty")
    
    print(f"Merging {len(point_clouds)} point clouds...")
    
    # Concatenate all points
    merged = np.vstack(point_clouds)
    print(f"  Total points before merging: {len(merged)}")
    
    if remove_duplicates:
        if not OPEN3D_AVAILABLE:
            print("  Warning: open3d not available, skipping duplicate removal")
        else:
            # Use voxel downsampling to remove duplicates
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(merged)
            pcd = pcd.voxel_down_sample(voxel_size=voxel_size)
            merged = np.asarray(pcd.points)
            print(f"  Total points after merging: {len(merged)}")
    
    return merged


def create_3d_map(point_clouds: List[np.ndarray],
                 output_path: Optional[str] = None,
                 resolution: float = 0.02) -> np.ndarray:
    """
    Create 3D map from multiple scans
    
    Args:
        point_clouds: List of point cloud arrays
        output_path: Optional path to save map
        resolution: Map resolution in meters
        
    Returns:
        Merged and processed point cloud
    """
    # Merge all scans
    map_points = merge_scans(point_clouds, voxel_size=resolution)
    
    if OPEN3D_AVAILABLE:
        # Create point cloud object
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(map_points)
        
        # Estimate normals
        print("Estimating normals...")
        pcd.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamKNN(knn=30)
        )
        
        # Orient normals consistently
        pcd.orient_normals_consistent_tangent_plane(k=15)
        
        if output_path:
            o3d.io.write_point_cloud(output_path, pcd)
            print(f"3D map saved to {output_path}")
        
        return np.asarray(pcd.points)
    else:
        print("Warning: open3d not available, skipping normal estimation")
        if output_path:
            np.save(output_path.replace('.ply', '.npy'), map_points)
            print(f"3D map saved to {output_path} (as .npy since open3d unavailable)")
        return map_points


def create_occupancy_grid(points: np.ndarray,
                         resolution: float = 0.1,
                         bounds: Optional[Tuple[float, float, float]] = None
                         ) -> np.ndarray:
    """
    Create 2D occupancy grid from point cloud (top-down view)
    
    Args:
        points: Nx3 point cloud
        resolution: Grid cell size in meters
        bounds: Optional (width, height, max_z) in meters
        
    Returns:
        2D numpy array representing occupancy grid
    """
    # Extract x, y coordinates
    x, y = points[:, 0], points[:, 1]
    
    if bounds:
        width, height, max_z = bounds
        # Filter by height
        mask = points[:, 2] <= max_z
        x, y = x[mask], y[mask]
    else:
        width = x.max() - x.min()
        height = y.max() - y.min()
    
    # Create grid
    grid_width = int(width / resolution) + 1
    grid_height = int(height / resolution) + 1
    grid = np.zeros((grid_height, grid_width), dtype=np.uint8)
    
    # Populate grid
    x_min, y_min = x.min(), y.min()
    x_indices = ((x - x_min) / resolution).astype(int)
    y_indices = ((y - y_min) / resolution).astype(int)
    
    # Clip to grid bounds
    x_indices = np.clip(x_indices, 0, grid_width - 1)
    y_indices = np.clip(y_indices, 0, grid_height - 1)
    
    grid[y_indices, x_indices] = 1
    
    return grid


def save_map(points: np.ndarray, 
            output_path: str,
            format: str = "ply"):
    """
    Save 3D map to file
    
    Args:
        points: Nx3 point cloud
        output_path: Output file path
        format: File format (ply, pcd, xyz)
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    if not output_path.endswith(f'.{format}'):
        output_path = f"{output_path}.{format}"
    
    if OPEN3D_AVAILABLE:
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        o3d.io.write_point_cloud(output_path, pcd)
        print(f"Map saved to {output_path}")
    else:
        # Fallback to numpy
        np_path = output_path.replace(f'.{format}', '.npy')
        np.save(np_path, points)
        print(f"Map saved to {np_path} (open3d not available)")


def load_map(file_path: str) -> np.ndarray:
    """
    Load 3D map from file
    
    Args:
        file_path: Path to point cloud file
        
    Returns:
        Nx3 numpy array
    """
    if file_path.endswith('.npy'):
        return np.load(file_path)
    elif OPEN3D_AVAILABLE:
        pcd = o3d.io.read_point_cloud(file_path)
        return np.asarray(pcd.points)
    else:
        raise ImportError("open3d is required to load point cloud files. Install with: pip install open3d")
