#!/usr/bin/env python3
"""
Simple LiDAR sensor test script

Tests connection to LiDAR sensor and captures a single scan for verification.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import numpy as np
from sensor.capture import LiDARSensor
from visualization.plotter import plot_2d_scan
import yaml


def test_sensor_connection():
    """Test basic sensor connection and capture"""
    
    print("="*60)
    print("LIDAR SENSOR CONNECTION TEST")
    print("="*60)
    print()
    
    # Load config
    with open("config/config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    sensor_config = config.get('sensor', {})
    port = sensor_config.get('port', '/dev/ttyUSB0')
    baudrate = sensor_config.get('baudrate', 115200)
    
    print(f"Configuration:")
    print(f"  Port: {port}")
    print(f"  Baudrate: {baudrate}")
    print()
    
    # Available ports help
    print("Common ports:")
    print("  macOS: /dev/tty.usbserial-*, /dev/tty.SLAB_USBtoUART")
    print("  Linux: /dev/ttyUSB0, /dev/ttyACM0")
    print("  Windows: COM3, COM4, COM5, etc.")
    print()
    print("Find your port:")
    print("  macOS/Linux: ls /dev/tty.*")
    print("  Windows: Check Device Manager")
    print()
    
    # Initialize sensor
    print("Initializing sensor...")
    sensor = LiDARSensor(port=port, baudrate=baudrate, timeout=2.0)
    
    # Test connection
    print("Attempting connection...")
    if sensor.connect():
        print("✓ Connection successful!")
        print()
        
        try:
            print("Capturing test scan (360 points)...")
            angles, distances = sensor.capture_scan(num_points=360, angle_step=1.0)
            
            print(f"✓ Scan captured successfully!")
            print(f"  Points captured: {len(distances)}")
            print(f"  Valid readings: {np.sum(distances > 0.1)}")
            print(f"  Distance range: {distances[distances > 0.1].min():.2f}m - {distances.max():.2f}m")
            print()
            
            # Save data
            output_file = "data/raw/sensor_test.npy"
            points = sensor.angles_distances_to_xyz(angles, distances)
            np.save(output_file, points)
            print(f"✓ Saved to {output_file}")
            print()
            
            # Visualize
            print("Generating visualization...")
            plot_2d_scan(angles, distances, title="LiDAR Sensor Test Scan",
                        save_path="output/sensor_test_scan.png")
            print("✓ Visualization saved to output/sensor_test_scan.png")
            print()
            
            print("="*60)
            print("TEST PASSED - Sensor is working correctly!")
            print("="*60)
            
        except Exception as e:
            print(f"✗ Error during scan: {e}")
            print()
            import traceback
            traceback.print_exc()
        
        finally:
            sensor.disconnect()
    
    else:
        print("✗ Connection failed")
        print()
        print("Troubleshooting steps:")
        print("  1. Check sensor power supply")
        print("  2. Verify USB cable connection")
        print("  3. Check port name is correct")
        print("  4. Try different USB port")
        print("  5. Check permissions:")
        print("     Linux: sudo chmod 666 /dev/ttyUSB0")
        print("     macOS: Usually no permission issues")
        print("  6. Check if another program is using the port")
        print()
        print("Testing with simulated data...")
        print()
        
        # Simulate for demo
        angles = np.linspace(0, 360, 360, endpoint=False)
        distances = 2.0 + 0.5 * np.sin(np.deg2rad(angles * 3))
        distances += np.random.normal(0, 0.05, len(distances))
        
        print(f"Simulated scan: {len(distances)} points")
        plot_2d_scan(angles, distances, title="Simulated LiDAR Scan (Test)",
                    save_path="output/simulated_test_scan.png")
        print("✓ Simulated visualization saved")


if __name__ == "__main__":
    test_sensor_connection()
