"""
Tests for processing module
"""

import pytest
import numpy as np
from processing.filters import (
    downsample_voxel,
    remove_outliers,
    filter_distance_range
)


def test_downsample_voxel():
    """Test voxel downsampling"""
    # Create dense point cloud
    points = np.random.rand(1000, 3) * 10
    
    downsampled = downsample_voxel(points, voxel_size=1.0)
    
    # Should have fewer points
    assert len(downsampled) < len(points)
    assert downsampled.shape[1] == 3


def test_distance_filtering():
    """Test distance range filtering"""
    # Create points at various distances
    points = np.array([
        [0.1, 0, 0],   # Too close
        [1.0, 0, 0],   # Valid
        [5.0, 0, 0],   # Valid
        [15.0, 0, 0],  # Too far
    ])
    
    filtered = filter_distance_range(points, min_dist=0.5, max_dist=10.0)
    
    assert len(filtered) == 2  # Only middle two points
    

def test_outlier_removal():
    """Test statistical outlier removal"""
    # Create main cluster with outliers
    cluster = np.random.randn(100, 3) * 0.1
    outliers = np.array([[10, 10, 10], [-10, -10, -10]])
    
    points = np.vstack([cluster, outliers])
    
    cleaned = remove_outliers(points, nb_neighbors=10, std_ratio=2.0)
    
    # Should remove outliers
    assert len(cleaned) < len(points)
    assert len(cleaned) >= len(cluster) - 10  # Allow some removal from cluster


def test_empty_point_cloud():
    """Test handling of empty point cloud"""
    points = np.array([]).reshape(0, 3)
    
    # Should handle gracefully
    filtered = filter_distance_range(points, min_dist=0.1, max_dist=10.0)
    assert len(filtered) == 0
