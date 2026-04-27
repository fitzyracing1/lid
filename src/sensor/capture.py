"""
LiDAR Sensor Interface Module

Handles communication with LiDAR sensor hardware and data acquisition.
"""

import serial
import numpy as np
import time
from typing import Optional, Tuple, List
import yaml


class LiDARSensor:
    """Interface for LiDAR close-range sensor"""
    
    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 115200, 
                 timeout: float = 1.0):
        """
        Initialize LiDAR sensor connection
        
        Args:
            port: Serial port for sensor connection
            baudrate: Communication baudrate
            timeout: Serial timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn: Optional[serial.Serial] = None
        self.is_connected = False
        
    def connect(self) -> bool:
        """
        Establish connection with LiDAR sensor
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self.is_connected = True
            print(f"Connected to LiDAR sensor on {self.port}")
            return True
        except serial.SerialException as e:
            print(f"Failed to connect: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Close connection to sensor"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.is_connected = False
            print("Disconnected from LiDAR sensor")
    
    def read_distance(self) -> Optional[float]:
        """
        Read single distance measurement from sensor
        
        Returns:
            Distance in meters, or None if read fails
        """
        if not self.is_connected or not self.serial_conn:
            print("Sensor not connected")
            return None
        
        try:
            # Read data from sensor (format depends on specific sensor)
            data = self.serial_conn.readline()
            # Parse distance value (example format)
            distance = float(data.decode().strip())
            return distance
        except Exception as e:
            print(f"Error reading distance: {e}")
            return None
    
    def capture_scan(self, num_points: int = 360, 
                    angle_step: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Capture a 360-degree scan
        
        Args:
            num_points: Number of measurement points
            angle_step: Angular step between measurements (degrees)
            
        Returns:
            Tuple of (angles, distances) as numpy arrays
        """
        if not self.is_connected:
            raise RuntimeError("Sensor not connected")
        
        angles = np.arange(0, num_points * angle_step, angle_step)
        distances = np.zeros(num_points)
        
        print(f"Capturing {num_points}-point scan...")
        for i in range(num_points):
            distance = self.read_distance()
            if distance is not None:
                distances[i] = distance
            else:
                distances[i] = 0.0  # Mark invalid readings
            
            # Small delay between readings
            time.sleep(0.01)
        
        print("Scan complete")
        return angles, distances
    
    def angles_distances_to_xyz(self, angles: np.ndarray, 
                                distances: np.ndarray,
                                z_height: float = 0.0) -> np.ndarray:
        """
        Convert polar coordinates to 3D Cartesian coordinates
        
        Args:
            angles: Array of angles in degrees
            distances: Array of distances in meters
            z_height: Height/elevation of scan plane
            
        Returns:
            Nx3 array of (x, y, z) points
        """
        # Convert angles to radians
        angles_rad = np.deg2rad(angles)
        
        # Calculate x, y coordinates
        x = distances * np.cos(angles_rad)
        y = distances * np.sin(angles_rad)
        z = np.full_like(x, z_height)
        
        # Stack into Nx3 array
        points = np.column_stack((x, y, z))
        
        # Filter out invalid points (distance = 0)
        valid_mask = distances > 0.1
        points = points[valid_mask]
        
        return points


def capture_scan(config_path: str = "config/config.yaml") -> np.ndarray:
    """
    Convenience function to capture a single scan
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Nx3 numpy array of point cloud data
    """
    # Load configuration
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    sensor_config = config.get('sensor', {})
    
    # Initialize sensor
    sensor = LiDARSensor(
        port=sensor_config.get('port', '/dev/ttyUSB0'),
        baudrate=sensor_config.get('baudrate', 115200),
        timeout=sensor_config.get('timeout', 1.0)
    )
    
    # Connect and capture
    if sensor.connect():
        try:
            num_points = int(sensor_config.get('angle_range', 360) / 
                           sensor_config.get('angle_resolution', 1.0))
            angles, distances = sensor.capture_scan(num_points=num_points)
            points = sensor.angles_distances_to_xyz(angles, distances)
            return points
        finally:
            sensor.disconnect()
    else:
        raise RuntimeError("Failed to connect to sensor")


def main():
    """Main entry point for sensor capture"""
    print("LiDAR Sensor Capture")
    print("=" * 40)
    
    try:
        points = capture_scan()
        print(f"Captured {len(points)} points")
        
        # Save to file
        output_file = "data/raw/scan.npy"
        np.save(output_file, points)
        print(f"Saved to {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
