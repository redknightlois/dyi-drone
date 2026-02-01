"""
PyVista-based rendering for drone 3D parts.

Generates static PNG images from multiple camera angles.
Uses VTK/PyVista for high-quality rendering with proper colors.

Usage:
    from render_images import render_part, render_assembly
    render_part(my_part, "output.png", camera='iso', color='#4682B4')
"""

import tempfile
from pathlib import Path

# Import pyvista with off-screen rendering
import pyvista as pv

# Camera position presets (normalized vectors)
CAMERA_PRESETS = {
    'iso': (1, 1, 0.7),         # Classic isometric view
    'top': (0, 0, 1),           # Top-down view (looking at XY plane)
    'front': (0, -1, 0),        # Front view (looking at XZ plane)
    'left': (-1, 0, 0),         # Left side view
    'right': (1, 0, 0),         # Right side view
    'rear': (0, 1, 0),          # Rear view
}

# Default rendering settings
DEFAULT_SIZE = (800, 600)
DEFAULT_BACKGROUND = '#F5F5F5'  # Light gray


def hex_to_rgb(hex_color):
    """Convert hex color string to RGB tuple (0-1 range)."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return (r, g, b)


def part_to_mesh(part):
    """
    Convert a build123d Part to a PyVista mesh.

    Uses temporary STL file as intermediate format.

    Args:
        part: build123d Part object

    Returns:
        pv.PolyData: PyVista mesh
    """
    from build123d import export_stl

    # Create temporary STL file
    with tempfile.NamedTemporaryFile(suffix='.stl', delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # Export part to STL
        export_stl(part, tmp_path)

        # Load STL into PyVista
        mesh = pv.read(tmp_path)

        return mesh
    finally:
        # Clean up temp file
        Path(tmp_path).unlink(missing_ok=True)


def setup_camera(plotter, camera_preset, bounds):
    """
    Set up camera position based on preset and mesh bounds.

    Args:
        plotter: PyVista plotter
        camera_preset: str, one of CAMERA_PRESETS keys
        bounds: mesh bounds (xmin, xmax, ymin, ymax, zmin, zmax)
    """
    # Get camera direction from preset
    if camera_preset in CAMERA_PRESETS:
        direction = CAMERA_PRESETS[camera_preset]
    else:
        direction = CAMERA_PRESETS['iso']

    # Calculate center and size of bounding box
    xmin, xmax, ymin, ymax, zmin, zmax = bounds
    center = (
        (xmin + xmax) / 2,
        (ymin + ymax) / 2,
        (zmin + zmax) / 2
    )

    # Calculate distance based on bounding box diagonal
    diagonal = ((xmax - xmin)**2 + (ymax - ymin)**2 + (zmax - zmin)**2)**0.5
    distance = diagonal * 1.8  # Factor for good framing

    # Normalize direction
    mag = (direction[0]**2 + direction[1]**2 + direction[2]**2)**0.5
    direction = (direction[0]/mag, direction[1]/mag, direction[2]/mag)

    # Calculate camera position
    camera_pos = (
        center[0] + direction[0] * distance,
        center[1] + direction[1] * distance,
        center[2] + direction[2] * distance
    )

    # Set up vector (Z-up for most views, Y-up for top view)
    if camera_preset == 'top':
        up = (0, 1, 0)
    else:
        up = (0, 0, 1)

    plotter.camera_position = [camera_pos, center, up]


def render_part(part, filepath, camera='iso', color='#4682B4', size=None, background=None):
    """
    Render a single part to PNG file.

    Args:
        part: build123d Part object
        filepath: str or Path, output PNG path
        camera: str, camera preset ('iso', 'top', 'front', 'left', 'right', 'rear')
        color: str, hex color for the part
        size: tuple (width, height) in pixels, defaults to 800x600
        background: str, hex color for background
    """
    if size is None:
        size = DEFAULT_SIZE
    if background is None:
        background = DEFAULT_BACKGROUND

    filepath = Path(filepath)

    # Convert part to mesh
    mesh = part_to_mesh(part)

    # Create off-screen plotter
    plotter = pv.Plotter(off_screen=True, window_size=size)
    plotter.set_background(hex_to_rgb(background))

    # Add mesh with color and smooth shading
    plotter.add_mesh(
        mesh,
        color=hex_to_rgb(color),
        smooth_shading=True,
        specular=0.3,
        specular_power=20,
        ambient=0.3,
    )

    # Set up camera
    setup_camera(plotter, camera, mesh.bounds)

    # Add subtle lighting
    plotter.enable_shadows()

    # Render and save
    plotter.screenshot(str(filepath))
    plotter.close()

    print(f"  Rendered: {filepath}")


def render_assembly(parts_with_colors, filepath, camera='iso', size=None, background=None):
    """
    Render multiple parts with different colors to PNG file.

    Args:
        parts_with_colors: list of (part_list, color) tuples
            Each part_list is a list of build123d Part objects
            color is a hex color string
        filepath: str or Path, output PNG path
        camera: str, camera preset
        size: tuple (width, height) in pixels
        background: str, hex color for background
    """
    if size is None:
        size = DEFAULT_SIZE
    if background is None:
        background = DEFAULT_BACKGROUND

    filepath = Path(filepath)

    # Create off-screen plotter
    plotter = pv.Plotter(off_screen=True, window_size=size)
    plotter.set_background(hex_to_rgb(background))

    # Track overall bounds
    all_bounds = None

    # Add all parts with their colors
    for part_list, color in parts_with_colors:
        rgb = hex_to_rgb(color)

        for part in part_list:
            mesh = part_to_mesh(part)

            # Update overall bounds
            if all_bounds is None:
                all_bounds = list(mesh.bounds)
            else:
                bounds = mesh.bounds
                all_bounds[0] = min(all_bounds[0], bounds[0])  # xmin
                all_bounds[1] = max(all_bounds[1], bounds[1])  # xmax
                all_bounds[2] = min(all_bounds[2], bounds[2])  # ymin
                all_bounds[3] = max(all_bounds[3], bounds[3])  # ymax
                all_bounds[4] = min(all_bounds[4], bounds[4])  # zmin
                all_bounds[5] = max(all_bounds[5], bounds[5])  # zmax

            plotter.add_mesh(
                mesh,
                color=rgb,
                smooth_shading=True,
                specular=0.3,
                specular_power=20,
                ambient=0.3,
            )

    # Set up camera based on combined bounds
    if all_bounds:
        setup_camera(plotter, camera, tuple(all_bounds))

    # Render and save
    plotter.screenshot(str(filepath))
    plotter.close()

    print(f"  Rendered: {filepath}")
