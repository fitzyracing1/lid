"""
3D surface reconstruction from point clouds
"""

import numpy as np
from typing import Optional

try:
    import open3d as o3d
    OPEN3D_AVAILABLE = True
except ImportError:
    OPEN3D_AVAILABLE = False


def build_mesh(points: np.ndarray,
              depth: int = 9,
              method: str = "poisson") -> tuple:
    """
    Build mesh surface from point cloud
    
    Args:
        points: Nx3 point cloud with normals
        depth: Reconstruction depth (higher = more detail)
        method: Reconstruction method ('poisson' or 'ball_pivoting')
        
    Returns:
        Tuple of (mesh, densities) for Poisson, or (mesh,) for ball pivoting
    """
    if not OPEN3D_AVAILABLE:
        raise ImportError("open3d is required for mesh building. Install with: pip install open3d")
    
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    
    # Estimate normals if not present
    if not pcd.has_normals():
        print("Estimating normals...")
        pcd.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamKNN(knn=30)
        )
        pcd.orient_normals_consistent_tangent_plane(k=15)
    
    print(f"Building mesh using {method} reconstruction...")
    
    if method == "poisson":
        # Poisson surface reconstruction
        mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
            pcd, depth=depth
        )
        return mesh, densities
    
    elif method == "ball_pivoting":
        # Ball pivoting algorithm
        distances = pcd.compute_nearest_neighbor_distance()
        avg_dist = np.mean(distances)
        radius = 3 * avg_dist
        
        mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
            pcd,
            o3d.utility.DoubleVector([radius, radius * 2])
        )
        return (mesh,)
    
    else:
        raise ValueError(f"Unknown method: {method}")


def extract_surfaces(points: np.ndarray,
                    alpha: float = 0.1):
    """
    Extract surfaces using alpha shapes
    
    Args:
        points: Nx3 point cloud
        alpha: Alpha parameter for shape extraction
        
    Returns:
        Triangle mesh
    """
    if not OPEN3D_AVAILABLE:
        raise ImportError("open3d is required for surface extraction. Install with: pip install open3d")
    
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    
    print("Extracting surfaces with alpha shapes...")
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(
        pcd, alpha
    )
    
def simplify_mesh(mesh, target_triangles: int = 10000):
    """
    Simplify mesh by reducing triangle count
    
    Args:
        mesh: Input triangle mesh
        target_triangles: Target number of triangles
        
    Returns:
        Simplified mesh
    """
    if not OPEN3D_AVAILABLE:
        raise ImportError("open3d is required for mesh simplification. Install with: pip install open3d")
    
    print(f"Simplifying mesh from {len(mesh.triangles)} to ~{target_triangles} triangles...")
    
    simplified = mesh.simplify_quadric_decimation(
        target_number_of_triangles=target_triangles
    )
    
    print(f"Simplified mesh has {len(simplified.triangles)} triangles")
    return simplified
    
    print(f"Simplified mesh has {len(simplified.triangles)} triangles")
    return simplified
def save_mesh(mesh, output_path: str):
    """
    Save mesh to file
    
    Args:
        mesh: Triangle mesh
        output_path: Output file path (.obj, .ply, .stl)
    """
    if not OPEN3D_AVAILABLE:
        raise ImportError("open3d is required to save mesh files. Install with: pip install open3d")
    
    o3d.io.write_triangle_mesh(output_path, mesh)
    print(f"Mesh saved to {output_path}")
    o3d.io.write_triangle_mesh(output_path, mesh)
    print(f"Mesh saved to {output_path}")
