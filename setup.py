from setuptools import setup, find_packages

setup(
    name="lidar-3d-mapping",
    version="0.1.0",
    description="LiDAR-based 3D mapping and point cloud processing system",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "open3d>=0.17.0",
        "matplotlib>=3.7.0",
        "plotly>=5.14.0",
        "pandas>=2.0.0",
        "h5py>=3.8.0",
        "pyserial>=3.5",
        "opencv-python>=4.7.0",
        "Pillow>=9.5.0",
        "tqdm>=4.65.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.3.0",
            "pytest-cov>=4.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "lidar-capture=sensor.capture:main",
            "lidar-process=processing.pipeline:main",
            "lidar-visualize=visualization.viewer:main",
        ],
    },
)
