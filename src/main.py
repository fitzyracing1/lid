"""
Main application entry point for LiDAR 3D Mapping System
"""

import argparse
import numpy as np
from pathlib import Path

from sensor.capture import capture_scan
from processing.pipeline import process_point_cloud, load_config
from visualization.viewer import view_point_cloud
from mapping.mapper import create_3d_map, save_map


def main():
    """Main application"""
    parser = argparse.ArgumentParser(
        description='LiDAR 3D Mapping System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Capture single scan
  python main.py capture --output data/raw/scan1.npy
  
  # Process existing scan
  python main.py process data/raw/scan1.npy --output data/processed/scan1.npy
  
  # Visualize point cloud
  python main.py view data/processed/scan1.npy
  
  # Create 3D map from multiple scans
  python main.py map data/processed/*.npy --output output/map.ply
        """
    )
    
    parser.add_argument('--config', '-c', default='config/config.yaml',
                       help='Configuration file path')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Capture command
    capture_parser = subparsers.add_parser('capture', help='Capture LiDAR scan')
    capture_parser.add_argument('--output', '-o', required=True,
                               help='Output file path')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process point cloud')
    process_parser.add_argument('input', help='Input point cloud file')
    process_parser.add_argument('--output', '-o', required=True,
                               help='Output file path')
    
    # View command
    view_parser = subparsers.add_parser('view', help='Visualize point cloud')
    view_parser.add_argument('input', help='Input point cloud file')
    
    # Map command
    map_parser = subparsers.add_parser('map', help='Create 3D map')
    map_parser.add_argument('inputs', nargs='+', help='Input point cloud files')
    map_parser.add_argument('--output', '-o', required=True,
                           help='Output map file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Load configuration
    config = load_config(args.config)
    
    # Execute command
    if args.command == 'capture':
        print("=" * 50)
        print("CAPTURING LIDAR SCAN")
        print("=" * 50)
        
        points = capture_scan(args.config)
        
        # Save raw data
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(output_path, points)
        
        print(f"\nCaptured {len(points)} points")
        print(f"Saved to {output_path}")
    
    elif args.command == 'process':
        print("=" * 50)
        print("PROCESSING POINT CLOUD")
        print("=" * 50)
        
        # Load input
        points = np.load(args.input)
        print(f"Loaded {len(points)} points from {args.input}")
        
        # Process
        processed = process_point_cloud(points, config)
        
        # Save output
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(output_path, processed)
        
        print(f"\nProcessed cloud has {len(processed)} points")
        print(f"Saved to {output_path}")
    
    elif args.command == 'view':
        print("=" * 50)
        print("VISUALIZING POINT CLOUD")
        print("=" * 50)
        
        # Load point cloud
        input_path = Path(args.input)
        if input_path.suffix == '.npy':
            points = np.load(input_path)
        else:
            import open3d as o3d
            pcd = o3d.io.read_point_cloud(str(input_path))
            points = np.asarray(pcd.points)
        
        print(f"Loaded {len(points)} points from {input_path}")
        
        # Visualize
        view_point_cloud(points, config=config, 
                        window_name=f"LiDAR Viewer - {input_path.name}")
    
    elif args.command == 'map':
        print("=" * 50)
        print("CREATING 3D MAP")
        print("=" * 50)
        
        # Load all input point clouds
        point_clouds = []
        for input_file in args.inputs:
            points = np.load(input_file)
            point_clouds.append(points)
            print(f"Loaded {len(points)} points from {input_file}")
        
        # Create map
        map_points = create_3d_map(
            point_clouds,
            output_path=args.output,
            resolution=config['mapping'].get('resolution', 0.02)
        )
        
        print(f"\n3D map created with {len(map_points)} points")
        print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
