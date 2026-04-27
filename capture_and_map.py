#!/usr/bin/env python3
"""
Real LiDAR Sensor Data Capture and Mapping Script

This script connects to a close-range LiDAR sensor, captures multiple scans
from different positions, and creates a 3D map.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import numpy as np
import time
from datetime import datetime
from sensor.capture import LiDARSensor
from processing.pipeline import process_point_cloud, load_config
from visualization.plotter import plot_2d_scan, plot_3d_scatter
from mapping.mapper import merge_scans, save_map

def capture_multiple_scans(sensor, num_scans=5, delay_between_scans=3):
    """
    Capture multiple scans with pauses between them
    
    Args:
        sensor: LiDARSensor instance
        num_scans: Number of scans to capture
        delay_between_scans: Seconds to wait between scans
    
    Returns:
        List of point cloud arrays
    """
    scans = []
    
    print(f"\n{'='*60}")
    print(f"CAPTURING {num_scans} SCANS")
    print(f"{'='*60}")
    print("\nMove the sensor to different positions between scans")
    print(f"You have {delay_between_scans} seconds between each scan\n")
    
    for i in range(num_scans):
        print(f"\n--- SCAN {i+1}/{num_scans} ---")
        
        if i > 0:
            print(f"Move sensor to new position...")
            for remaining in range(delay_between_scans, 0, -1):
                print(f"  Starting in {remaining}...", end='\r')
                time.sleep(1)
            print()
        
        try:
            # Capture scan
            angles, distances = sensor.capture_scan(num_points=360, angle_step=1.0)
            
            # Convert to 3D points
            points = sensor.angles_distances_to_xyz(angles, distances, z_height=i * 0.1)
            
            print(f"✓ Captured {len(points)} points")
            
            # Save raw scan
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            raw_file = f"data/raw/scan_{i+1}_{timestamp}.npy"
            np.save(raw_file, points)
            print(f"✓ Saved to {raw_file}")
            
            scans.append(points)
            
            # Quick visualization of this scan
            if len(points) > 0:
                print(f"  Distance range: {distances.min():.2f}m - {distances.max():.2f}m")
            
        except Exception as e:
            print(f"✗ Error capturing scan {i+1}: {e}")
            continue
    
    return scans


def process_and_map(scans, config):
    """
    Process scans and create 3D map
    
    Args:
        scans: List of raw point cloud arrays
        config: Configuration dictionary
    
    Returns:
        Merged map point cloud
    """
    if len(scans) == 0:
        print("\n✗ No scans to process")
        return None
    
    print(f"\n{'='*60}")
    print(f"PROCESSING {len(scans)} SCANS")
    print(f"{'='*60}\n")
    
    processed_scans = []
    
    for i, scan in enumerate(scans, 1):
        print(f"Processing scan {i}/{len(scans)}...")
        
        try:
            # Process point cloud
            processed = process_point_cloud(scan, config)
            processed_scans.append(processed)
            
            # Save processed scan
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            processed_file = f"data/processed/scan_{i}_{timestamp}.npy"
            np.save(processed_file, processed)
            print(f"✓ Saved to {processed_file}\n")
            
        except Exception as e:
            print(f"✗ Error processing scan {i}: {e}\n")
            continue
    
    if len(processed_scans) == 0:
        print("\n✗ No scans processed successfully")
        return None
    
    # Create 3D map
    print(f"\n{'='*60}")
    print("CREATING 3D MAP")
    print(f"{'='*60}\n")
    
    try:
        map_points = merge_scans(processed_scans, remove_duplicates=True, voxel_size=0.05)
        
        # Save map
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        map_file = f"output/lidar_map_{timestamp}.npy"
        np.save(map_file, map_points)
        print(f"\n✓ 3D map created with {len(map_points)} points")
        print(f"✓ Saved to {map_file}")
        
        return map_points
        
    except Exception as e:
        print(f"\n✗ Error creating map: {e}")
        return None


def main():
    """Main execution"""
    print(f"\n{'='*60}")
    print("LIDAR CLOSE-RANGE SENSOR MAPPING")
    print(f"{'='*60}\n")
    
    # Load configuration
    config = load_config("config/config.yaml")
    sensor_config = config.get('sensor', {})
    
    # Configuration
    PORT = sensor_config.get('port', '/dev/ttyUSB0')
    BAUDRATE = sensor_config.get('baudrate', 115200)
    NUM_SCANS = 4  # Number of scans to capture from different positions
    
    print(f"Configuration:")
    print(f"  Sensor Port: {PORT}")
    print(f"  Baudrate: {BAUDRATE}")
    print(f"  Number of Scans: {NUM_SCANS}")
    print()
    
    # Initialize sensor
    print("Initializing LiDAR sensor...")
    sensor = LiDARSensor(port=PORT, baudrate=BAUDRATE, timeout=1.0)
    
    # Connect to sensor
    if not sensor.connect():
        print("\n✗ Failed to connect to sensor")
        print("\nTroubleshooting:")
        print("  1. Check sensor is powered on")
        print("  2. Verify USB connection")
        print("  3. Check port name (try: ls /dev/tty.*)")
        print("  4. Check permissions (may need: sudo chmod 666 /dev/ttyUSB0)")
        print("\nNote: This example will continue with simulated data for demo purposes")
        
        # Simulate data for demonstration
        print("\n--- USING SIMULATED DATA ---")
        scans = []
        for i in range(NUM_SCANS):
            angles = np.linspace(0, 360, 360, endpoint=False)
            distances = 2.0 + 0.5 * np.sin(np.deg2rad(angles * 3)) + np.random.normal(0, 0.1, len(angles))
            distances = np.clip(distances, 0.5, 5.0)
            points = sensor.angles_distances_to_xyz(angles, distances, z_height=i * 0.1)
            scans.append(points)
            print(f"  Simulated scan {i+1}: {len(points)} points")
    else:
        try:
            # Capture multiple scans
            scans = capture_multiple_scans(sensor, num_scans=NUM_SCANS, delay_between_scans=3)
        finally:
            sensor.disconnect()
    
    # Process and create map
    map_points = process_and_map(scans, config)
    
    if map_points is not None:
        # Visualize results
        print(f"\n{'='*60}")
        print("VISUALIZATION")
        print(f"{'='*60}\n")
        
        print("Generating visualizations...")
        
        try:
            # 3D scatter plot
            plot_3d_scatter(map_points, title="LiDAR 3D Map", 
                          save_path="output/map_3d_view.png")
            
            # Show statistics
            print(f"\nMap Statistics:")
            print(f"  Total Points: {len(map_points)}")
            print(f"  X Range: {map_points[:,0].min():.2f}m to {map_points[:,0].max():.2f}m")
            print(f"  Y Range: {map_points[:,1].min():.2f}m to {map_points[:,1].max():.2f}m")
            print(f"  Z Range: {map_points[:,2].min():.2f}m to {map_points[:,2].max():.2f}m")
            
        except Exception as e:
            print(f"✗ Visualization error: {e}")
    
    print(f"\n{'='*60}")
    print("MAPPING COMPLETE")
    print(f"{'='*60}\n")
    print("Output files saved in:")
    print("  - data/raw/      (raw scans)")
    print("  - data/processed/ (processed scans)")
    print("  - output/        (final map)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nMapping interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
