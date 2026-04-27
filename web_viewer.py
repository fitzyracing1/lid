#!/usr/bin/env python3
"""
Interactive Web-Based 3D Point Cloud Viewer

This script creates an interactive HTML viewer for LiDAR point cloud data
using Plotly. The viewer allows rotation, zoom, and panning with the mouse.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import argparse

def create_interactive_viewer(points, title="LiDAR Point Cloud", color_by='z', point_size=2):
    """
    Create an interactive 3D viewer using Plotly
    
    Args:
        points: Nx3 numpy array of point cloud
        title: Title for the visualization
        color_by: How to color points ('z', 'distance', 'height', or 'uniform')
        point_size: Size of points
    
    Returns:
        Plotly figure object
    """
    # Calculate colors based on option
    if color_by == 'z':
        colors = points[:, 2]
        colorbar_title = 'Height (m)'
    elif color_by == 'distance':
        colors = np.sqrt(points[:, 0]**2 + points[:, 1]**2 + points[:, 2]**2)
        colorbar_title = 'Distance (m)'
    elif color_by == 'height':
        colors = points[:, 2] - np.min(points[:, 2])
        colorbar_title = 'Relative Height (m)'
    else:  # uniform
        colors = np.ones(len(points))
        colorbar_title = ''
    
    # Create 3D scatter plot
    trace = go.Scatter3d(
        x=points[:, 0],
        y=points[:, 1],
        z=points[:, 2],
        mode='markers',
        marker=dict(
            size=point_size,
            color=colors,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title=colorbar_title),
            opacity=0.8
        ),
        text=[f'X: {x:.3f}<br>Y: {y:.3f}<br>Z: {z:.3f}' 
              for x, y, z in points],
        hoverinfo='text'
    )
    
    # Create layout
    layout = go.Layout(
        title=dict(
            text=f'{title}<br>({len(points):,} points)',
            x=0.5,
            xanchor='center'
        ),
        scene=dict(
            xaxis_title='X (m)',
            yaxis_title='Y (m)',
            zaxis_title='Z (m)',
            aspectmode='data',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        ),
        hovermode='closest',
        showlegend=False,
        height=800
    )
    
    fig = go.Figure(data=[trace], layout=layout)
    
    return fig

def create_multi_view(points, title="LiDAR Point Cloud"):
    """
    Create a multi-view visualization with 3D, top-down, and side views
    
    Args:
        points: Nx3 numpy array of point cloud
        title: Title for the visualization
    
    Returns:
        Plotly figure object
    """
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        specs=[
            [{'type': 'scatter3d', 'rowspan': 2}, {'type': 'scatter'}],
            [None, {'type': 'scatter'}]
        ],
        subplot_titles=('3D View', 'Top-Down (X-Y)', 'Side View (X-Z)'),
        vertical_spacing=0.1,
        horizontal_spacing=0.1
    )
    
    colors = points[:, 2]
    
    # 3D view
    fig.add_trace(
        go.Scatter3d(
            x=points[:, 0],
            y=points[:, 1],
            z=points[:, 2],
            mode='markers',
            marker=dict(
                size=2,
                color=colors,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title='Height (m)', x=0.4),
                opacity=0.8
            ),
            name='3D'
        ),
        row=1, col=1
    )
    
    # Top-down view (X-Y)
    fig.add_trace(
        go.Scatter(
            x=points[:, 0],
            y=points[:, 1],
            mode='markers',
            marker=dict(
                size=3,
                color=colors,
                colorscale='Viridis',
                showscale=False,
                opacity=0.6
            ),
            name='Top-Down'
        ),
        row=1, col=2
    )
    
    # Side view (X-Z)
    fig.add_trace(
        go.Scatter(
            x=points[:, 0],
            y=points[:, 2],
            mode='markers',
            marker=dict(
                size=3,
                color=colors,
                colorscale='Viridis',
                showscale=False,
                opacity=0.6
            ),
            name='Side View'
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title_text=f'{title} - Multi-View ({len(points):,} points)',
        height=800,
        showlegend=False
    )
    
    # Update axes
    fig.update_xaxes(title_text="X (m)", row=1, col=2)
    fig.update_yaxes(title_text="Y (m)", row=1, col=2)
    fig.update_xaxes(title_text="X (m)", row=2, col=2)
    fig.update_yaxes(title_text="Z (m)", row=2, col=2)
    
    fig.update_scenes(
        xaxis_title='X (m)',
        yaxis_title='Y (m)',
        zaxis_title='Z (m)',
        aspectmode='data'
    )
    
    return fig

def create_density_map(points, grid_size=0.1):
    """
    Create a 2D density heatmap of the point cloud (bird's eye view)
    
    Args:
        points: Nx3 numpy array of point cloud
        grid_size: Size of grid cells in meters
    
    Returns:
        Plotly figure object
    """
    # Create 2D histogram
    x_bins = np.arange(points[:, 0].min(), points[:, 0].max() + grid_size, grid_size)
    y_bins = np.arange(points[:, 1].min(), points[:, 1].max() + grid_size, grid_size)
    
    H, xedges, yedges = np.histogram2d(points[:, 0], points[:, 1], bins=[x_bins, y_bins])
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=H.T,
        x=xedges,
        y=yedges,
        colorscale='Hot',
        colorbar=dict(title='Point Density')
    ))
    
    fig.update_layout(
        title=f'Point Cloud Density Map (Grid: {grid_size}m)',
        xaxis_title='X (m)',
        yaxis_title='Y (m)',
        height=700,
        yaxis=dict(scaleanchor="x", scaleratio=1)
    )
    
    return fig

def create_height_histogram(points):
    """
    Create a histogram of point heights
    
    Args:
        points: Nx3 numpy array of point cloud
    
    Returns:
        Plotly figure object
    """
    fig = go.Figure(data=[go.Histogram(
        x=points[:, 2],
        nbinsx=50,
        marker_color='steelblue',
        opacity=0.7
    )])
    
    fig.update_layout(
        title='Height Distribution',
        xaxis_title='Height (m)',
        yaxis_title='Number of Points',
        showlegend=False,
        height=400
    )
    
    return fig

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Interactive web-based 3D viewer for LiDAR data')
    parser.add_argument('input', help='Input point cloud file (.npy)')
    parser.add_argument('--output', default='output/viewer.html', help='Output HTML file')
    parser.add_argument('--view', choices=['single', 'multi', 'density', 'height', 'all'], 
                       default='all', help='View type')
    parser.add_argument('--color-by', choices=['z', 'distance', 'height', 'uniform'],
                       default='z', help='How to color points')
    parser.add_argument('--point-size', type=float, default=2.0, help='Point size')
    parser.add_argument('--grid-size', type=float, default=0.1, 
                       help='Grid size for density map (m)')
    parser.add_argument('--auto-open', action='store_true', 
                       help='Automatically open in browser')
    
    args = parser.parse_args()
    
    # Load point cloud
    print(f"Loading point cloud from {args.input}...")
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"Error: File not found: {args.input}")
        return
    
    points = np.load(input_path)
    print(f"  Loaded {len(points):,} points")
    
    # Calculate statistics
    print(f"\nPoint Cloud Statistics:")
    print(f"  X range: {points[:, 0].min():.3f} to {points[:, 0].max():.3f} m")
    print(f"  Y range: {points[:, 1].min():.3f} to {points[:, 1].max():.3f} m")
    print(f"  Z range: {points[:, 2].min():.3f} to {points[:, 2].max():.3f} m")
    print(f"  Centroid: ({points[:, 0].mean():.3f}, {points[:, 1].mean():.3f}, {points[:, 2].mean():.3f})")
    
    # Create visualization(s)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if args.view == 'single':
        print(f"\nCreating single 3D view...")
        fig = create_interactive_viewer(points, 
                                       title=input_path.stem,
                                       color_by=args.color_by,
                                       point_size=args.point_size)
        fig.write_html(str(output_path), auto_open=args.auto_open)
        print(f"  Saved to: {output_path}")
        
    elif args.view == 'multi':
        print(f"\nCreating multi-view...")
        fig = create_multi_view(points, title=input_path.stem)
        fig.write_html(str(output_path), auto_open=args.auto_open)
        print(f"  Saved to: {output_path}")
        
    elif args.view == 'density':
        print(f"\nCreating density map...")
        fig = create_density_map(points, grid_size=args.grid_size)
        fig.write_html(str(output_path), auto_open=args.auto_open)
        print(f"  Saved to: {output_path}")
        
    elif args.view == 'height':
        print(f"\nCreating height histogram...")
        fig = create_height_histogram(points)
        fig.write_html(str(output_path), auto_open=args.auto_open)
        print(f"  Saved to: {output_path}")
        
    else:  # all
        print(f"\nCreating comprehensive view...")
        
        # Create all visualizations
        fig_3d = create_interactive_viewer(points, 
                                          title=input_path.stem,
                                          color_by=args.color_by,
                                          point_size=args.point_size)
        fig_multi = create_multi_view(points, title=input_path.stem)
        fig_density = create_density_map(points, grid_size=args.grid_size)
        fig_height = create_height_histogram(points)
        
        # Save individual files
        base_path = output_path.parent / output_path.stem
        
        fig_3d.write_html(str(base_path) + '_3d.html')
        print(f"  3D view saved to: {base_path}_3d.html")
        
        fig_multi.write_html(str(base_path) + '_multi.html')
        print(f"  Multi-view saved to: {base_path}_multi.html")
        
        fig_density.write_html(str(base_path) + '_density.html')
        print(f"  Density map saved to: {base_path}_density.html")
        
        fig_height.write_html(str(base_path) + '_height.html')
        print(f"  Height histogram saved to: {base_path}_height.html")
        
        # Create index page
        index_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>LiDAR Point Cloud Viewer - {input_path.stem}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .stats {{
            background: white;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .views {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .view-card {{
            background: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.2s;
        }}
        .view-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }}
        .view-card h3 {{
            color: #4CAF50;
            margin-top: 0;
        }}
        .view-card a {{
            display: inline-block;
            padding: 10px 20px;
            background: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 3px;
            margin-top: 10px;
        }}
        .view-card a:hover {{
            background: #45a049;
        }}
        .stat-row {{
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px solid #eee;
        }}
        .stat-label {{
            font-weight: bold;
            color: #666;
        }}
    </style>
</head>
<body>
    <h1>🗺️ LiDAR Point Cloud Viewer</h1>
    <p>Dataset: <strong>{input_path.stem}</strong></p>
    
    <div class="stats">
        <h2>Point Cloud Statistics</h2>
        <div class="stat-row">
            <span class="stat-label">Total Points:</span>
            <span>{len(points):,}</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">X Range:</span>
            <span>{points[:, 0].min():.3f} to {points[:, 0].max():.3f} m</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Y Range:</span>
            <span>{points[:, 1].min():.3f} to {points[:, 1].max():.3f} m</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Z Range:</span>
            <span>{points[:, 2].min():.3f} to {points[:, 2].max():.3f} m</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Centroid:</span>
            <span>({points[:, 0].mean():.3f}, {points[:, 1].mean():.3f}, {points[:, 2].mean():.3f})</span>
        </div>
    </div>
    
    <h2>Available Views</h2>
    <div class="views">
        <div class="view-card">
            <h3>3D Interactive View</h3>
            <p>Rotate, zoom, and pan the full 3D point cloud</p>
            <a href="{base_path.name}_3d.html">Open 3D View</a>
        </div>
        <div class="view-card">
            <h3>Multi-View Layout</h3>
            <p>See 3D, top-down, and side views simultaneously</p>
            <a href="{base_path.name}_multi.html">Open Multi-View</a>
        </div>
        <div class="view-card">
            <h3>Density Map</h3>
            <p>Bird's eye view showing point density</p>
            <a href="{base_path.name}_density.html">Open Density Map</a>
        </div>
        <div class="view-card">
            <h3>Height Distribution</h3>
            <p>Histogram of point heights</p>
            <a href="{base_path.name}_height.html">Open Histogram</a>
        </div>
    </div>
</body>
</html>
"""
        
        index_path = base_path.parent / f"{base_path.name}.html"
        with open(index_path, 'w') as f:
            f.write(index_html)
        
        print(f"\n  Index page saved to: {index_path}")
        
        if args.auto_open:
            import webbrowser
            webbrowser.open(f'file://{index_path.absolute()}')
    
    print("\n✓ Visualization complete!")
    print(f"\nTo view, open the HTML file(s) in your web browser")

if __name__ == "__main__":
    main()
