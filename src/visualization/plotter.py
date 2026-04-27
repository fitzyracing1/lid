"""
2D plotting utilities for LiDAR data
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional


def plot_2d_scan(angles: np.ndarray, distances: np.ndarray,
                title: str = "LiDAR 2D Scan",
                save_path: Optional[str] = None):
    """
    Plot 2D polar scan data
    
    Args:
        angles: Array of angles in degrees
        distances: Array of distances in meters
        title: Plot title
        save_path: Optional path to save figure
    """
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='polar')
    
    # Convert angles to radians
    angles_rad = np.deg2rad(angles)
    
    # Plot
    ax.scatter(angles_rad, distances, c=distances, cmap='viridis', 
              s=10, alpha=0.6)
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_title(title, pad=20)
    ax.set_ylim(0, distances.max() * 1.1)
    
    plt.colorbar(ax.collections[0], label='Distance (m)', pad=0.1)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")
    
    plt.show()


def plot_distance_histogram(distances: np.ndarray,
                           bins: int = 50,
                           title: str = "Distance Distribution",
                           save_path: Optional[str] = None):
    """
    Plot histogram of distance measurements
    
    Args:
        distances: Array of distance values
        bins: Number of histogram bins
        title: Plot title
        save_path: Optional path to save figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.hist(distances, bins=bins, color='steelblue', alpha=0.7, edgecolor='black')
    ax.set_xlabel('Distance (m)')
    ax.set_ylabel('Frequency')
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    
    # Add statistics
    mean_dist = np.mean(distances)
    median_dist = np.median(distances)
    ax.axvline(mean_dist, color='red', linestyle='--', 
              label=f'Mean: {mean_dist:.2f}m')
    ax.axvline(median_dist, color='green', linestyle='--',
              label=f'Median: {median_dist:.2f}m')
    ax.legend()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")
    
    plt.show()


def plot_3d_scatter(points: np.ndarray,
                   colors: Optional[np.ndarray] = None,
                   title: str = "3D Point Cloud",
                   save_path: Optional[str] = None):
    """
    Simple 3D scatter plot of point cloud
    
    Args:
        points: Nx3 numpy array
        colors: Optional color array
        title: Plot title
        save_path: Optional path to save figure
    """
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')
    
    if colors is None:
        # Color by height
        colors = points[:, 2]
    
    scatter = ax.scatter(points[:, 0], points[:, 1], points[:, 2],
                        c=colors, cmap='viridis', s=1, alpha=0.6)
    
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_zlabel('Z (m)')
    ax.set_title(title)
    
    # Equal aspect ratio
    max_range = np.array([
        points[:, 0].max() - points[:, 0].min(),
        points[:, 1].max() - points[:, 1].min(),
        points[:, 2].max() - points[:, 2].min()
    ]).max() / 2.0
    
    mid_x = (points[:, 0].max() + points[:, 0].min()) * 0.5
    mid_y = (points[:, 1].max() + points[:, 1].min()) * 0.5
    mid_z = (points[:, 2].max() + points[:, 2].min()) * 0.5
    
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)
    
    plt.colorbar(scatter, label='Height (m)', pad=0.1)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")
    
    plt.show()
