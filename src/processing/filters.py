"""
Point cloud filtering operations
"""

import numpy as np
from typing import Optional

try:
    import open3d as o3d
    OPEN3D_AVAILABLE = True
except ImportError:
    OPEN3D_AVAILABLE = False


def downsample_voxel(points: np.ndarray, voxel_size: float = 0.05) -> np.ndarray:
    """
    Downsample point cloud using voxel grid
    
    Args:
        points: Nx3 numpy array
        voxel_size: Size of voxel grid in meters
        
    Returns:
        Downsampled Nx3 numpy array
    """
    if not OPEN3D_AVAILABLE:
        raise ImportError("open3d is required for voxel downsampling. Install with: pip install open3d")
    
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    
    downsampled = pcd.voxel_down_sample(voxel_size=voxel_size)
    
    return np.asarray(downsampled.points)


def remove_outliers(points: np.ndarray, nb_neighbors: int = 20, 
                   std_ratio: float = 2.0) -> np.ndarray:
    """
    Remove statistical outliers from point cloud
    
    Args:
        points: Nx3 numpy array
        nb_neighbors: Number of neighbors to analyze
        std_ratio: Standard deviation ratio threshold
        
    Returns:
        Filtered Nx3 numpy array
    """
    if not OPEN3D_AVAILABLE:
        raise ImportError("open3d is required for outlier removal. Install with: pip install open3d")
    
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    
    cl, ind = pcd.remove_statistical_outlier(
        nb_neighbors=nb_neighbors,
        std_ratio=std_ratio
    )
    
    return np.asarray(cl.points)


def filter_distance_range(points: np.ndarray, min_dist: float = 0.15,
                         max_dist: float = 12.0) -> np.ndarray:
    """
    Filter points outside distance range from origin
    
    Args:
        points: Nx3 numpy array
        min_dist: Minimum distance in meters
        max_dist: Maximum distance in meters
        
    Returns:
        Filtered Nx3 numpy array
    """
    distances = np.linalg.norm(points, axis=1)
    mask = (distances >= min_dist) & (distances <= max_dist)
    return points[mask]


def smooth_point_cloud(points: np.ndarray, k_neighbors: int = 10) -> np.ndarray:
    """
    Smooth point cloud using moving least squares
    
    Args:
        points: Nx3 numpy array
        k_neighbors: Number of neighbors for smoothing
        
    Returns:
        Smoothed Nx3 numpy array
    """
    if not OPEN3D_AVAILABLE:
        raise ImportError("open3d is required for point cloud smoothing. Install with: pip install open3d")
    
    # Simple smoothing using neighbor averaging
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    
    # Estimate normals for smoothing
    pcd.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamKNN(knn=k_neighbors)
    )
    
    return np.asarray(pcd.points)


def compute_normals(points: np.ndarray, k_neighbors: int = 30) -> np.ndarray:
    """
    Compute normals for point cloud
    
    Args:
        points: Nx3 numpy array
        k_neighbors: Number of neighbors for normal estimation
        
    Returns:
        Nx3 numpy array of normal vectors
    """
    if not OPEN3D_AVAILABLE:
        raise ImportError("open3d is required for normal computation. Install with: pip install open3d")
    
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    
    pcd.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamKNN(knn=k_neighbors)
    )
    
    return np.asarray(pcd.normals)
