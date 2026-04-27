"""
Tests for sensor module
"""

import pytest
import numpy as np
from sensor.capture import LiDARSensor
from sensor.calibration import apply_calibration


def test_sensor_initialization():
    """Test sensor initialization"""
    sensor = LiDARSensor(port="/dev/ttyUSB0", baudrate=115200)
    assert sensor.port == "/dev/ttyUSB0"
    assert sensor.baudrate == 115200
    assert not sensor.is_connected


def test_angles_to_xyz_conversion():
    """Test polar to Cartesian conversion"""
    sensor = LiDARSensor()
    
    # Test simple case: 4 cardinal directions
    angles = np.array([0, 90, 180, 270])
    distances = np.array([1.0, 1.0, 1.0, 1.0])
    
    points = sensor.angles_distances_to_xyz(angles, distances, z_height=0.0)
    
    assert points.shape[1] == 3  # x, y, z
    assert len(points) == 4
    
    # Check approximate values (accounting for floating point)
    assert np.isclose(points[0, 0], 1.0, atol=0.01)  # x at 0°
    assert np.isclose(points[0, 1], 0.0, atol=0.01)  # y at 0°


def test_calibration():
    """Test calibration application"""
    distances = np.array([1.0, 2.0, 3.0, 4.0])
    scale = 1.1
    offset = 0.05
    
    calibrated = apply_calibration(distances, scale, offset)
    
    expected = distances * scale + offset
    assert np.allclose(calibrated, expected)


def test_invalid_distance_filtering():
    """Test that zero distances are filtered"""
    sensor = LiDARSensor()
    
    angles = np.array([0, 90, 180, 270])
    distances = np.array([1.0, 0.0, 2.0, 0.05])  # Include invalid readings
    
    points = sensor.angles_distances_to_xyz(angles, distances)
    
    # Should filter out points with distance <= 0.1
    assert len(points) == 2  # Only 1.0 and 2.0 remain
