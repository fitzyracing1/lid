#!/usr/bin/env python3
"""
Real-time LiDAR Data Capture with Live Visualization

This script captures LiDAR scans and displays them in real-time as they're acquired.
Each scan is shown immediately, allowing you to verify sensor positioning.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time
from datetime import datetime
from sensor.capture import LiDARSensor
from processing.pipeline import process_point_cloud, load_config
from visualization.plotter import plot_3d_scatter
from mapping.mapper import merge_scans, save_map

class RealtimeVisualizer:
    """Real-time visualization of LiDAR scans"""
    
    def __init__(self):
        """Initialize the visualizer"""
        self.fig = plt.figure(figsize=(15, 5))
        self.ax1 = self.fig.add_subplot(131, projection='3d')
        self.ax2 = self.fig.add_subplot(132)
        self.ax3 = self.fig.add_subplot(133, projection='3d')
        
        self.current_scan = None
        self.all_scans = []
        self.merged_map = None
        
        self.ax1.set_title('Current Scan (3D)')
        self.ax2.set_title('Current Scan (Top-Down)')
        self.ax3.set_title('Merged Map (3D)')
        
        plt.tight_layout()
    
    def update_current_scan(self, points):
        """Update visualization with new scan"""
        self.current_scan = points
        self.all_scans.append(points)
        
        # Clear previous plots
        self.ax1.clear()
        self.ax2.clear()
        
        # Plot 3D view of current scan
        self.ax1.scatter(points[:, 0], points[:, 1], points[:, 2], 
                        c=points[:, 2], cmap='viridis', s=1)
        self.ax1.set_xlabel('X (m)')
        self.ax1.set_ylabel('Y (m)')
        self.ax1.set_zlabel('Z (m)')
        self.ax1.set_title(f'Current Scan (3D) - {len(points)} points')
        
        # Plot top-down view
        self.ax2.scatter(points[:, 0], points[:, 1], 
                        c=points[:, 2], cmap='viridis', s=1)
        self.ax2.set_xlabel('X (m)')
        self.ax2.set_ylabel('Y (m)')
        self.ax2.set_title(f'Current Scan (Top-Down)')
        self.ax2.axis('equal')
        self.ax2.grid(True, alpha=0.3)
        
        plt.draw()
        plt.pause(0.1)
    
    def update_merged_map(self):
        """Update the merged map visualization"""
        if len(self.all_scans) > 0:
            self.merged_map = np.vstack(self.all_scans)
            
            self.ax3.clear()
            self.ax3.scatter(self.merged_map[:, 0], 
                           self.merged_map[:, 1], 
                           self.merged_map[:, 2],
                           c=self.merged_map[:, 2], cmap='plasma', s=1, alpha=0.5)
            self.ax3.set_xlabel('X (m)')
            self.ax3.set_ylabel('Y (m)')
            self.ax3.set_zlabel('Z (m)')
            self.ax3.set_title(f'Merged Map - {len(self.merged_map)} points')
            
            plt.draw()
            plt.pause(0.1)
    
    def show(self):
        """Display the visualization"""
        plt.show(block=False)

def capture_with_live_view(sensor, num_scans=4, delay_between_scans=3):
    """
    Capture multiple scans with live visualization
    
    Args:
        sensor: LiDARSensor instance
        num_scans: Number of scans to capture
        delay_between_scans: Seconds to wait between scans
    
    Returns:
        List of point cloud arrays
    """
    viz = RealtimeVisualizer()
    viz.show()
    
    scans = []
    config = load_config()
    
    print(f"\n{'='*60}")
    print(f"REAL-TIME CAPTURE - {num_scans} SCANS")
    print(f"{'='*60}")
    print("\nWatch the visualization update as each scan is captured!")
    print("Move the sensor to different positions between scans\n")
    
    for i in range(num_scans):
        print(f"\n--- SCAN {i+1}/{num_scans} ---")
        
        if i > 0:
            print(f"Move sensor to new position...")
            for remaining in range(delay_between_scans, 0, -1):
                print(f"  Starting in {remaining}...", end='\r')
                time.sleep(1)
            print()
        
        print("Capturing scan...", end='', flush=True)
        scan = sensor.capture_scan()
        
        if scan is None or len(scan) == 0:
            print(" FAILED - No data received")
            continue
        
        print(f" ✓ Captured {len(scan)} points")
        
        # Process the scan
        print("Processing...", end='', flush=True)
        processed = process_point_cloud(scan, config)
        print(f" ✓ {len(processed)} points after processing")
        
        # Save raw data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_path = Path("data/raw") / f"scan_{i+1}_{timestamp}.npy"
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(raw_path, scan)
        
        # Save processed data
        proc_path = Path("data/processed") / f"scan_{i+1}_{timestamp}.npy"
        proc_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(proc_path, processed)
        
        scans.append(processed)
        
        # Update visualization
        print("Updating visualization...", end='', flush=True)
        viz.update_current_scan(processed)
        viz.update_merged_map()
        print(" ✓")
    
    print(f"\n{'='*60}")
    print(f"CAPTURE COMPLETE")
    print(f"{'='*60}\n")
    
    # Keep final visualization open
    print("Close the visualization window to continue...")
    plt.show()
    
    return scans

def main():
    """Main execution"""
    config = load_config()
    
    # Initialize sensor
    print("\n" + "="*60)
    print("LIDAR REAL-TIME CAPTURE & MAPPING")
    print("="*60)
    print(f"\nConfiguration:")
    print(f"  Port: {config['sensor']['port']}")
    print(f"  Baudrate: {config['sensor']['baudrate']}")
    print(f"  Number of scans: {config['mapping']['num_scans']}")
    print()
    
    sensor = LiDARSensor(
        port=config['sensor']['port'],
        baudrate=config['sensor']['baudrate']
    )
    
    if not sensor.connect():
        print("⚠ Could not connect to sensor - using simulated data")
        # Create simulated sensor for demo
        from sensor.capture import create_simulated_scan
        class SimulatedSensor:
            def capture_scan(self):
                return create_simulated_scan(num_points=360, noise_level=0.02)
        sensor = SimulatedSensor()
    else:
        print("✓ Sensor connected successfully")
    
    # Capture scans with live visualization
    scans = capture_with_live_view(
        sensor,
        num_scans=config['mapping']['num_scans'],
        delay_between_scans=3
    )
    
    if len(scans) == 0:
        print("Error: No scans captured")
        return
    
    # Create 3D map
    print("\nCreating 3D map...")
    merged_map = merge_scans(scans)
    print(f"  Merged {len(scans)} scans into map with {len(merged_map)} points")
    
    # Save map
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    map_path = output_dir / f"lidar_map_{timestamp}.npy"
    save_map(merged_map, str(map_path))
    print(f"  Map saved to: {map_path}")
    
    # Create final visualization
    print("\nGenerating final visualization...")
    viz_path = output_dir / "map_3d_view.png"
    plot_3d_scatter(merged_map, title="Final 3D Map", save_path=str(viz_path))
    print(f"  Visualization saved to: {viz_path}")
    
    print("\n" + "="*60)
    print("MAPPING COMPLETE!")
    print("="*60)
    print(f"\nResults:")
    print(f"  Total scans: {len(scans)}")
    print(f"  Total points: {len(merged_map)}")
    print(f"  Output: {map_path}")
    print()

if __name__ == "__main__":
    main()
