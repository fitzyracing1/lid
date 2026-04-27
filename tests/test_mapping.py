"""
Tests for mapping module
"""

import pytest
import numpy as np
from mapping.mapper import merge_scans, create_occupancy_grid


def test_merge_scans():
    """Test merging multiple point clouds"""
    scan1 = np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0]])
    scan2 = np.array([[0, 1, 0], [1, 1, 0], [2, 1, 0]])
    scan3 = np.array([[0, 2, 0], [1, 2, 0], [2, 2, 0]])
    
    merged = merge_scans([scan1, scan2, scan3], remove_duplicates=False)
    
    assert len(merged) == 9  # 3 + 3 + 3
    assert merged.shape[1] == 3


def test_merge_with_deduplication():
    """Test merging with duplicate removal"""
    scan1 = np.array([[0, 0, 0], [1, 0, 0]])
    scan2 = np.array([[0, 0, 0], [2, 0, 0]])  # Duplicate point
    
    merged = merge_scans([scan1, scan2], remove_duplicates=True, voxel_size=0.01)
    
    # Should remove duplicate
    assert len(merged) <= 3


def test_occupancy_grid():
    """Test 2D occupancy grid creation"""
    # Create simple point cloud
    points = np.array([
        [0, 0, 0],
        [1, 0, 0],
        [0, 1, 0],
        [1, 1, 0],
    ])
    
    grid = create_occupancy_grid(points, resolution=0.5)
    
    assert grid.ndim == 2
    assert grid.dtype == np.uint8
    assert np.any(grid == 1)  # Should have occupied cells


def test_empty_merge():
    """Test merging empty list"""
    with pytest.raises(ValueError):
        merge_scans([])
