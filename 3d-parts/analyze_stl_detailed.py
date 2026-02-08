"""
Detailed STL analysis to understand box structure.
"""

import numpy as np
import trimesh


def analyze_box_structure(filepath):
    """Analyze the box structure from the reference STL."""
    print("=" * 70)
    print(f"DETAILED ANALYSIS: {filepath}")
    print("=" * 70)

    tmesh = trimesh.load(filepath)
    vertices = tmesh.vertices

    # Overall dimensions
    x_min, x_max = vertices[:, 0].min(), vertices[:, 0].max()
    y_min, y_max = vertices[:, 1].min(), vertices[:, 1].max()
    z_min, z_max = vertices[:, 2].min(), vertices[:, 2].max()

    print(f"\nOVERALL DIMENSIONS:")
    print(f"  X: {x_min:.2f} to {x_max:.2f} (length: {x_max - x_min:.2f} mm)")
    print(f"  Y: {y_min:.2f} to {y_max:.2f} (width: {y_max - y_min:.2f} mm)")
    print(f"  Z: {z_min:.2f} to {z_max:.2f} (height: {z_max - z_min:.2f} mm)")

    # Unique Z levels
    z_levels = np.unique(np.round(vertices[:, 2], 1))
    print(f"\nZ LEVELS: {[float(z) for z in z_levels]}")

    # Analyze each Z level to find features
    print(f"\n--- LAYER-BY-LAYER ANALYSIS ---")

    for z in z_levels:
        mask = np.abs(vertices[:, 2] - z) < 0.15
        pts = vertices[mask]
        if len(pts) < 4:
            continue

        print(f"\nZ = {z:.1f} mm ({len(pts)} vertices):")

        # Find outer boundary
        outer_x_min, outer_x_max = pts[:, 0].min(), pts[:, 0].max()
        outer_y_min, outer_y_max = pts[:, 1].min(), pts[:, 1].max()
        outer_width = outer_x_max - outer_x_min
        outer_height = outer_y_max - outer_y_min

        print(f"  Outer bounds: {outer_width:.1f} x {outer_height:.1f} mm")
        print(f"    X: [{outer_x_min:.1f}, {outer_x_max:.1f}]")
        print(f"    Y: [{outer_y_min:.1f}, {outer_y_max:.1f}]")

        # Find inner boundary by looking at points not on the outer edge
        inner_pts = pts[(pts[:, 0] > outer_x_min + 0.5) &
                        (pts[:, 0] < outer_x_max - 0.5) &
                        (pts[:, 1] > outer_y_min + 0.5) &
                        (pts[:, 1] < outer_y_max - 0.5)]

        if len(inner_pts) > 4:
            inner_x_min, inner_x_max = inner_pts[:, 0].min(), inner_pts[:, 0].max()
            inner_y_min, inner_y_max = inner_pts[:, 1].min(), inner_pts[:, 1].max()
            inner_width = inner_x_max - inner_x_min
            inner_height = inner_y_max - inner_y_min

            wall_thickness_x = (outer_width - inner_width) / 2
            wall_thickness_y = (outer_height - inner_height) / 2

            print(f"  Inner bounds: {inner_width:.1f} x {inner_height:.1f} mm")
            print(f"  Wall thickness: X={wall_thickness_x:.1f} mm, Y={wall_thickness_y:.1f} mm")

    # Slice analysis for more detail
    print(f"\n--- SLICE ANALYSIS (Cross-sections) ---")

    # Base level (Z=0)
    analyze_slice(tmesh, 0.4, "Base (Z=0.4)")

    # Mid level
    analyze_slice(tmesh, 3.4, "Mid (Z=3.4)")

    # Top level
    analyze_slice(tmesh, 6.0, "Top (Z=6.0)")


def analyze_slice(tmesh, z, label):
    """Analyze a horizontal slice at given Z."""
    try:
        section = tmesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        if section is None:
            return

        path, _ = section.to_planar()
        if not hasattr(path, 'polygons_full') or len(path.polygons_full) == 0:
            return

        print(f"\n{label}:")
        for i, poly in enumerate(path.polygons_full):
            bounds = poly.bounds
            width = bounds[2] - bounds[0]
            height = bounds[3] - bounds[1]
            print(f"  Polygon {i+1}: {width:.1f} x {height:.1f} mm, area={poly.area:.1f} mm²")

            # Check for holes
            if hasattr(poly, 'interiors'):
                for j, hole in enumerate(list(poly.interiors)):
                    coords = np.array(hole.coords)
                    h_bounds = (coords[:, 0].min(), coords[:, 1].min(),
                                coords[:, 0].max(), coords[:, 1].max())
                    h_width = h_bounds[2] - h_bounds[0]
                    h_height = h_bounds[3] - h_bounds[1]
                    center_x = (h_bounds[0] + h_bounds[2]) / 2
                    center_y = (h_bounds[1] + h_bounds[3]) / 2

                    # Determine if it's a circle or rectangle
                    perimeter = coords.shape[0]
                    if perimeter > 16:  # More vertices = likely circle
                        shape = "circle"
                        diameter = max(h_width, h_height)
                        print(f"    Hole {j+1}: {shape}, d={diameter:.1f}mm at ({center_x:.1f}, {center_y:.1f})")
                    else:
                        shape = "rect"
                        print(f"    Hole {j+1}: {shape}, {h_width:.1f}x{h_height:.1f}mm at ({center_x:.1f}, {center_y:.1f})")

    except Exception as e:
        print(f"  Slice error: {e}")


def find_ventilation_slots(tmesh):
    """Find ventilation slot patterns in the mesh."""
    print(f"\n--- VENTILATION SLOT DETECTION ---")

    vertices = tmesh.vertices

    # Slots are typically on the Y walls (front/back)
    # Look for vertices at Y extremes that form patterns

    # Front wall (Y max)
    y_max = vertices[:, 1].max()
    front_pts = vertices[np.abs(vertices[:, 1] - y_max) < 0.5]

    if len(front_pts) > 10:
        print(f"\nFront wall (Y={y_max:.1f}):")
        # Find X positions of vertical features
        x_vals = np.sort(np.unique(np.round(front_pts[:, 0], 1)))
        print(f"  X positions: {[float(x) for x in x_vals[:20]]}...")

        # Find gaps (slots) by looking for large jumps in X
        x_diff = np.diff(x_vals)
        slot_indices = np.where(x_diff > 1.5)[0]
        if len(slot_indices) > 0:
            print(f"  Potential slots at X gaps: {[float(x_vals[i]) for i in slot_indices]}")

    # Back wall (Y min)
    y_min = vertices[:, 1].min()
    back_pts = vertices[np.abs(vertices[:, 1] - y_min) < 0.5]

    if len(back_pts) > 10:
        print(f"\nBack wall (Y={y_min:.1f}):")
        x_vals = np.sort(np.unique(np.round(back_pts[:, 0], 1)))
        print(f"  X positions: {[float(x) for x in x_vals[:20]]}...")


if __name__ == "__main__":
    filepath = "3d-parts/components/power-source-box-schematic.stl"
    tmesh = trimesh.load(filepath)

    analyze_box_structure(filepath)
    find_ventilation_slots(tmesh)

    # Export key dimensions
    print("\n" + "=" * 70)
    print("EXTRACTED DIMENSIONS FOR BUILD123D")
    print("=" * 70)

    v = tmesh.vertices

    print("""
# Based on STL analysis - Power Source Box dimensions

# Overall box dimensions (from bounding box)
BOX_LENGTH = 58.2   # mm (X)
BOX_WIDTH = 36.8    # mm (Y)
BOX_HEIGHT = 6.8    # mm (Z)

# Base/floor
BASE_THICKNESS = 0.8  # mm (from Z=0 to Z=0.8)

# Wall structure (from cross-section analysis)
WALL_THICKNESS = 0.8  # mm (outer - inner)/2

# Inner cavity (from Z=1.6 cross-section: 56.6 x 35.2)
INNER_LENGTH = 56.6   # mm
INNER_WIDTH = 35.2    # mm

# Display window area (elevated platform around Z=4.6)
# Cross-section at Z=4.5-5.1 shows 56.0 x 34.0 inner area
DISPLAY_PLATFORM_Z = 4.6  # mm from base

# Note: The render image shows:
# - 4 ventilation slots on each long side
# - A rectangular display window
# - Mounting tabs at corners with holes
# - The box has walls going up, not just a flat tray
""")
