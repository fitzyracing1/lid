"""
Point cloud registration and alignment
"""

import numpy as np
from typing import Tuple

try:
    import open3d as o3d
    OPEN3D_AVAILABLE = True
except ImportError:
    OPEN3D_AVAILABLE = False


def icp_registration(source: np.ndarray, target: np.ndarray,
                    threshold: float = 0.02, 
                    max_iteration: int = 50) -> Tuple[np.ndarray, float]:
    """
    Perform ICP (Iterative Closest Point) registration
    
    Args:
        source: Source point cloud (Nx3)
        target: Target point cloud (Nx3)
        threshold: Distance threshold
        max_iteration: Maximum iterations
        
    Returns:
        Tuple of (transformation_matrix, fitness_score)
    """
    if not OPEN3D_AVAILABLE:
        raise ImportError("open3d is required for ICP registration. Install with: pip install open3d")
    
    source_pcd = o3d.geometry.PointCloud()
    source_pcd.points = o3d.utility.Vector3dVector(source)
    
    target_pcd = o3d.geometry.PointCloud()
    target_pcd.points = o3d.utility.Vector3dVector(target)
    
    # Initial alignment (identity)
    trans_init = np.eye(4)
    
    # Perform ICP
    reg_result = o3d.pipelines.registration.registration_icp(
        source_pcd, target_pcd, threshold, trans_init,
        o3d.pipelines.registration.TransformationEstimationPointToPoint(),
        o3d.pipelines.registration.ICPConvergenceCriteria(
            max_iteration=max_iteration
        )
    )
    
    return reg_result.transformation, reg_result.fitness


def register_point_clouds(point_clouds: list, 
                         threshold: float = 0.02) -> list:
    """
    Register multiple point clouds into a single coordinate system
    
    Args:
        point_clouds: List of Nx3 numpy arrays
        threshold: ICP distance threshold
        
    Returns:
        List of registered point clouds
    """
    if len(point_clouds) < 2:
        return point_clouds
    
    registered = [point_clouds[0]]  # First cloud is reference
    cumulative_transform = np.eye(4)
    
    print(f"Registering {len(point_clouds)} point clouds...")
    
    for i in range(1, len(point_clouds)):
        print(f"Registering cloud {i+1}/{len(point_clouds)}...")
        
        # Register to previous cloud
        transform, fitness = icp_registration(
            point_clouds[i], 
            registered[-1], 
            threshold=threshold
        )
        
        print(f"  Fitness: {fitness:.4f}")
        
        # Apply transformation
        homogeneous = np.hstack([
            point_clouds[i],
            np.ones((len(point_clouds[i]), 1))
        ])
        transformed = (transform @ homogeneous.T).T[:, :3]
        
        registered.append(transformed)
    
    return registered


def apply_transformation(points: np.ndarray, 
                        transformation: np.ndarray) -> np.ndarray:
    """
    Apply 4x4 transformation matrix to points
    
    Args:
        points: Nx3 numpy array
        transformation: 4x4 transformation matrix
        
    Returns:
        Transformed Nx3 numpy array
    """
    homogeneous = np.hstack([points, np.ones((len(points), 1))])
    transformed = (transformation @ homogeneous.T).T[:, :3]
    return transformed
