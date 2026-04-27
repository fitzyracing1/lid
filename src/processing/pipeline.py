"""
Processing pipeline for point cloud data
"""

import numpy as np
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from .filters import (
    downsample_voxel, 
    remove_outliers, 
    filter_distance_range
)


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def process_point_cloud(points: np.ndarray, 
                       config: Optional[Dict[str, Any]] = None) -> np.ndarray:
    """
    Apply full processing pipeline to point cloud
    
    Args:
        points: Raw Nx3 point cloud
        config: Configuration dictionary (optional)
        
    Returns:
        Processed Nx3 point cloud
    """
    if config is None:
        config = load_config()
    
    processing_config = config.get('processing', {})
    
    print(f"Processing point cloud with {len(points)} points...")
    
    # Step 1: Distance filtering
    print("  Filtering by distance range...")
    points = filter_distance_range(
        points,
        min_dist=processing_config.get('min_distance', 0.15),
        max_dist=processing_config.get('max_distance', 12.0)
    )
    print(f"    {len(points)} points remaining")
    
    # Step 2: Downsampling
    print("  Downsampling...")
    voxel_size = processing_config.get('voxel_size', 0.05)
    try:
        points = downsample_voxel(points, voxel_size=voxel_size)
        print(f"    {len(points)} points after downsampling")
    except ImportError as e:
        print(f"    Skipping downsampling: {e}")
    
    # Step 3: Outlier removal
    print("  Removing outliers...")
    outlier_config = processing_config.get('outlier_removal', {})
    try:
        points = remove_outliers(
            points,
            nb_neighbors=outlier_config.get('nb_neighbors', 20),
            std_ratio=outlier_config.get('std_ratio', 2.0)
        )
        print(f"    {len(points)} points after outlier removal")
    except ImportError as e:
        print(f"    Skipping outlier removal: {e}")
    
    print("Processing complete!")
    return points


def batch_process(input_dir: str, output_dir: str, 
                 config_path: str = "config/config.yaml"):
    """
    Process multiple point cloud files in batch
    
    Args:
        input_dir: Directory containing input .npy files
        output_dir: Directory for processed outputs
        config_path: Path to configuration file
    """
    config = load_config(config_path)
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all .npy files
    input_files = list(input_path.glob("*.npy"))
    
    print(f"Processing {len(input_files)} files...")
    print("=" * 50)
    
    for i, input_file in enumerate(input_files, 1):
        print(f"\n[{i}/{len(input_files)}] Processing {input_file.name}")
        
        # Load point cloud
        points = np.load(input_file)
        
        # Process
        processed = process_point_cloud(points, config)
        
        # Save
        output_file = output_path / input_file.name
        np.save(output_file, processed)
        print(f"  Saved to {output_file}")
    
    print("\n" + "=" * 50)
    print("Batch processing complete!")


def main():
    """Main entry point for processing pipeline"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process LiDAR point clouds')
    parser.add_argument('input', help='Input file or directory')
    parser.add_argument('--output', '-o', default='data/processed',
                       help='Output directory')
    parser.add_argument('--config', '-c', default='config/config.yaml',
                       help='Configuration file')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    if input_path.is_file():
        # Process single file
        points = np.load(input_path)
        processed = process_point_cloud(points, load_config(args.config))
        
        output_file = Path(args.output) / input_path.name
        output_file.parent.mkdir(parents=True, exist_ok=True)
        np.save(output_file, processed)
        print(f"Saved to {output_file}")
        
    elif input_path.is_dir():
        # Batch process directory
        batch_process(str(input_path), args.output, args.config)
    else:
        print(f"Error: {input_path} not found")


if __name__ == "__main__":
    main()
