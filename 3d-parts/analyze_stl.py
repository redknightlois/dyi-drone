"""
Analyze reference STL using RANSAC to detect primitive shapes.

Extracts dimensions from power-source-box-schematic.stl for reverse-engineering
the design into build123d CSG primitives.
"""

import numpy as np
from stl import mesh
import pyransac3d as pyrsc
from collections import defaultdict
import trimesh


def load_stl_points(filepath):
    """Load STL and extract unique vertices as point cloud."""
    stl_mesh = mesh.Mesh.from_file(filepath)
    # Flatten triangles to points
    points = stl_mesh.vectors.reshape(-1, 3)
    # Remove duplicates
    points = np.unique(points, axis=0)
    return points, stl_mesh


def analyze_bounding_box(points):
    """Get overall dimensions from point cloud."""
    min_coords = points.min(axis=0)
    max_coords = points.max(axis=0)
    dimensions = max_coords - min_coords
    center = (min_coords + max_coords) / 2
    return {
        'min': min_coords,
        'max': max_coords,
        'dimensions': dimensions,
        'center': center
    }


def detect_z_levels(points, tolerance=0.3):
    """Find distinct Z levels in the model (for layer detection)."""
    z_values = points[:, 2]
    z_unique = np.unique(np.round(z_values / tolerance) * tolerance)
    return sorted(z_unique)


def detect_planes(points, max_planes=10, thresh=0.1, min_inlier_ratio=0.02):
    """Detect planar surfaces using RANSAC."""
    detected_planes = []
    remaining_points = points.copy()
    min_inliers = int(len(points) * min_inlier_ratio)

    plane_detector = pyrsc.Plane()

    for _ in range(max_planes):
        if len(remaining_points) < min_inliers:
            break

        try:
            equation, inliers = plane_detector.fit(remaining_points, thresh=thresh)
            if len(inliers) < min_inliers:
                break

            inlier_points = remaining_points[inliers]
            plane_info = {
                'equation': equation,  # [a, b, c, d] for ax + by + cz + d = 0
                'normal': equation[:3],
                'num_points': len(inliers),
                'centroid': inlier_points.mean(axis=0),
                'bounds': {
                    'min': inlier_points.min(axis=0),
                    'max': inlier_points.max(axis=0)
                }
            }
            detected_planes.append(plane_info)

            # Remove inliers for next iteration
            mask = np.ones(len(remaining_points), dtype=bool)
            mask[inliers] = False
            remaining_points = remaining_points[mask]

        except Exception as e:
            print(f"Plane detection error: {e}")
            break

    return detected_planes


def detect_cylinders(points, max_cylinders=20, thresh=0.1, min_inlier_ratio=0.005):
    """Detect cylindrical features (holes, posts) using RANSAC."""
    detected_cylinders = []
    remaining_points = points.copy()
    min_inliers = max(int(len(points) * min_inlier_ratio), 20)

    cylinder_detector = pyrsc.Cylinder()

    for _ in range(max_cylinders):
        if len(remaining_points) < min_inliers:
            break

        try:
            center, axis, radius, inliers = cylinder_detector.fit(
                remaining_points, thresh=thresh, maxIteration=1000
            )

            if len(inliers) < min_inliers:
                break

            # Filter out unreasonably large cylinders (likely false positives)
            if radius > 10:  # More than 10mm radius is too large for holes/posts
                # Remove inliers and continue
                mask = np.ones(len(remaining_points), dtype=bool)
                mask[inliers] = False
                remaining_points = remaining_points[mask]
                continue

            inlier_points = remaining_points[inliers]
            z_min = inlier_points[:, 2].min()
            z_max = inlier_points[:, 2].max()

            cylinder_info = {
                'center': center,
                'axis': axis,
                'radius': radius,
                'diameter': radius * 2,
                'num_points': len(inliers),
                'z_range': (z_min, z_max),
                'height': z_max - z_min
            }
            detected_cylinders.append(cylinder_info)

            # Remove inliers
            mask = np.ones(len(remaining_points), dtype=bool)
            mask[inliers] = False
            remaining_points = remaining_points[mask]

        except Exception as e:
            print(f"Cylinder detection error: {e}")
            break

    return detected_cylinders


def analyze_cross_sections(points, z_levels):
    """Analyze cross-sections at each Z level to find feature dimensions."""
    cross_sections = {}

    for z in z_levels:
        # Get points near this Z level
        mask = np.abs(points[:, 2] - z) < 0.5
        section_points = points[mask]

        if len(section_points) > 10:
            cross_sections[z] = {
                'num_points': len(section_points),
                'x_range': (section_points[:, 0].min(), section_points[:, 0].max()),
                'y_range': (section_points[:, 1].min(), section_points[:, 1].max()),
                'x_span': section_points[:, 0].max() - section_points[:, 0].min(),
                'y_span': section_points[:, 1].max() - section_points[:, 1].min()
            }

    return cross_sections


def cluster_cylinders_by_position(cylinders, xy_tolerance=1.0):
    """Group cylinders that are at similar XY positions (same hole at different Z)."""
    if not cylinders:
        return []

    clusters = []
    used = set()

    for i, cyl in enumerate(cylinders):
        if i in used:
            continue

        cluster = [cyl]
        used.add(i)

        for j, other in enumerate(cylinders):
            if j in used:
                continue

            # Check if XY positions are similar
            dx = abs(cyl['center'][0] - other['center'][0])
            dy = abs(cyl['center'][1] - other['center'][1])

            if dx < xy_tolerance and dy < xy_tolerance:
                cluster.append(other)
                used.add(j)

        # Merge cluster info
        avg_x = np.mean([c['center'][0] for c in cluster])
        avg_y = np.mean([c['center'][1] for c in cluster])
        avg_radius = np.mean([c['radius'] for c in cluster])
        z_min = min(c['z_range'][0] for c in cluster)
        z_max = max(c['z_range'][1] for c in cluster)

        clusters.append({
            'x': avg_x,
            'y': avg_y,
            'radius': avg_radius,
            'diameter': avg_radius * 2,
            'z_min': z_min,
            'z_max': z_max,
            'height': z_max - z_min,
            'num_detections': len(cluster)
        })

    return clusters


def analyze_stl(filepath):
    """Main analysis function."""
    print("=" * 70)
    print(f"ANALYZING: {filepath}")
    print("=" * 70)

    # Load point cloud
    points, stl_mesh = load_stl_points(filepath)
    print(f"\nLoaded {len(points)} unique vertices")

    # Bounding box
    bbox = analyze_bounding_box(points)
    print(f"\n--- BOUNDING BOX ---")
    print(f"Dimensions: {bbox['dimensions'][0]:.2f} x {bbox['dimensions'][1]:.2f} x {bbox['dimensions'][2]:.2f} mm")
    print(f"Min corner: ({bbox['min'][0]:.2f}, {bbox['min'][1]:.2f}, {bbox['min'][2]:.2f})")
    print(f"Max corner: ({bbox['max'][0]:.2f}, {bbox['max'][1]:.2f}, {bbox['max'][2]:.2f})")
    print(f"Center: ({bbox['center'][0]:.2f}, {bbox['center'][1]:.2f}, {bbox['center'][2]:.2f})")

    # Z levels
    z_levels = detect_z_levels(points, tolerance=0.3)
    print(f"\n--- Z LEVELS (horizontal layers) ---")
    for z in z_levels:
        print(f"  Z = {z:.2f} mm")

    # Cross sections
    print(f"\n--- CROSS SECTIONS AT Z LEVELS ---")
    cross_sections = analyze_cross_sections(points, z_levels)
    for z, section in sorted(cross_sections.items()):
        print(f"  Z={z:.1f}mm: {section['x_span']:.1f} x {section['y_span']:.1f} mm ({section['num_points']} pts)")

    # Detect planes
    print(f"\n--- DETECTED PLANES ---")
    planes = detect_planes(points, max_planes=8, thresh=0.15)
    for i, plane in enumerate(planes):
        normal = plane['normal']
        # Classify plane orientation
        if abs(normal[2]) > 0.9:
            orientation = "horizontal (XY)"
        elif abs(normal[0]) > 0.9:
            orientation = "vertical (YZ)"
        elif abs(normal[1]) > 0.9:
            orientation = "vertical (XZ)"
        else:
            orientation = "angled"

        centroid = plane['centroid']
        bounds = plane['bounds']
        print(f"  Plane {i+1}: {orientation}")
        print(f"    Centroid: ({centroid[0]:.2f}, {centroid[1]:.2f}, {centroid[2]:.2f})")
        print(f"    Size: {bounds['max'][0]-bounds['min'][0]:.1f} x {bounds['max'][1]-bounds['min'][1]:.1f} mm")
        print(f"    Points: {plane['num_points']}")

    # Detect cylinders
    print(f"\n--- DETECTED CYLINDERS (holes/posts) ---")
    cylinders = detect_cylinders(points, max_cylinders=15, thresh=0.08)

    # Cluster by position
    cylinder_clusters = cluster_cylinders_by_position(cylinders)
    cylinder_clusters.sort(key=lambda c: c['diameter'], reverse=True)

    for i, cyl in enumerate(cylinder_clusters):
        print(f"  Cylinder {i+1}:")
        print(f"    Position: ({cyl['x']:.2f}, {cyl['y']:.2f}) mm")
        print(f"    Diameter: {cyl['diameter']:.2f} mm (radius: {cyl['radius']:.2f})")
        print(f"    Z range: {cyl['z_min']:.2f} to {cyl['z_max']:.2f} mm (height: {cyl['height']:.2f})")

    # Summary for CSG reconstruction
    print("\n" + "=" * 70)
    print("SUGGESTED BUILD123D DIMENSIONS")
    print("=" * 70)
    print(f"""
# Overall tray dimensions
TRAY_LENGTH = {bbox['dimensions'][0]:.1f}  # mm (X)
TRAY_WIDTH = {bbox['dimensions'][1]:.1f}   # mm (Y)
TRAY_HEIGHT = {bbox['dimensions'][2]:.1f}   # mm (Z)

# Z levels for layer construction
Z_LEVELS = {[round(z, 1) for z in z_levels]}

# Detected cylindrical features (holes/posts)
CYLINDERS = [""")
    for cyl in cylinder_clusters:
        print(f"    {{'x': {cyl['x']:.1f}, 'y': {cyl['y']:.1f}, 'dia': {cyl['diameter']:.1f}, 'z_min': {cyl['z_min']:.1f}, 'z_max': {cyl['z_max']:.1f}}},")
    print("]")

    return {
        'bbox': bbox,
        'z_levels': z_levels,
        'cross_sections': cross_sections,
        'planes': planes,
        'cylinders': cylinder_clusters
    }


def analyze_with_trimesh(filepath):
    """Use trimesh for more detailed geometric analysis."""
    print("\n" + "=" * 70)
    print("TRIMESH DETAILED ANALYSIS")
    print("=" * 70)

    tmesh = trimesh.load(filepath)
    print(f"\nMesh info:")
    print(f"  Vertices: {len(tmesh.vertices)}")
    print(f"  Faces: {len(tmesh.faces)}")
    print(f"  Is watertight: {tmesh.is_watertight}")
    print(f"  Volume: {tmesh.volume:.2f} mm³" if tmesh.is_watertight else "  Volume: N/A (not watertight)")

    # Analyze boundary edges to find holes and cutouts
    print(f"\n--- EDGE ANALYSIS ---")

    # Get unique edges
    edges = tmesh.edges_unique
    edge_lengths = tmesh.edges_unique_length

    # Find vertices at different Z levels
    vertices = tmesh.vertices
    z_vals = np.unique(np.round(vertices[:, 2], 1))

    print(f"\nUnique Z levels: {list(z_vals)}")

    # For each Z level, find the outline
    print(f"\n--- SLICE ANALYSIS ---")
    for z in z_vals:
        if z < 0 or z > 7:
            continue

        try:
            # Create a slice at this Z level
            slice_2d = tmesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
            if slice_2d is not None:
                # Get 2D path
                path_2d, transform = slice_2d.to_planar()
                if hasattr(path_2d, 'polygons_full') and len(path_2d.polygons_full) > 0:
                    print(f"\n  Z = {z:.1f} mm:")
                    for i, polygon in enumerate(path_2d.polygons_full):
                        bounds = polygon.bounds  # (minx, miny, maxx, maxy)
                        width = bounds[2] - bounds[0]
                        height = bounds[3] - bounds[1]
                        area = polygon.area
                        print(f"    Polygon {i+1}: {width:.1f} x {height:.1f} mm, area={area:.1f} mm²")

                        # Check for holes (interior rings)
                        if hasattr(polygon, 'interiors') and len(polygon.interiors) > 0:
                            print(f"      Interior holes: {len(polygon.interiors)}")
                            for j, hole in enumerate(polygon.interiors):
                                h_bounds = hole.bounds
                                h_width = h_bounds[2] - h_bounds[0]
                                h_height = h_bounds[3] - h_bounds[1]
                                # Calculate centroid of hole
                                h_coords = np.array(hole.coords)
                                h_center = h_coords.mean(axis=0)
                                print(f"        Hole {j+1}: {h_width:.1f} x {h_height:.1f} mm at ({h_center[0]:.1f}, {h_center[1]:.1f})")
        except Exception as e:
            pass  # Skip levels that fail

    # Convex hull analysis for overall shape
    print(f"\n--- CONVEX HULL ---")
    hull = tmesh.convex_hull
    hull_bounds = hull.bounds
    print(f"  Bounds: X[{hull_bounds[0][0]:.1f}, {hull_bounds[1][0]:.1f}], "
          f"Y[{hull_bounds[0][1]:.1f}, {hull_bounds[1][1]:.1f}], "
          f"Z[{hull_bounds[0][2]:.1f}, {hull_bounds[1][2]:.1f}]")

    return tmesh


def find_rectangular_features(filepath):
    """Analyze the mesh to find rectangular features and holes."""
    print("\n" + "=" * 70)
    print("RECTANGULAR FEATURE DETECTION")
    print("=" * 70)

    tmesh = trimesh.load(filepath)
    vertices = tmesh.vertices

    # Find all distinct Z levels more carefully
    z_precision = 0.1
    z_unique = np.unique(np.round(vertices[:, 2] / z_precision) * z_precision)
    print(f"\nDistinct Z levels: {[f'{z:.1f}' for z in z_unique]}")

    features = []

    # Analyze each significant Z level
    significant_z = [0.0, 0.8, 1.6, 4.8, 6.8]  # Based on earlier analysis

    for z in significant_z:
        # Get vertices near this Z
        mask = np.abs(vertices[:, 2] - z) < 0.3
        level_verts = vertices[mask]

        if len(level_verts) < 10:
            continue

        # Find bounding rectangle
        x_min, x_max = level_verts[:, 0].min(), level_verts[:, 0].max()
        y_min, y_max = level_verts[:, 1].min(), level_verts[:, 1].max()

        print(f"\nZ = {z:.1f} mm:")
        print(f"  Bounding rect: [{x_min:.1f}, {x_max:.1f}] x [{y_min:.1f}, {y_max:.1f}]")
        print(f"  Dimensions: {x_max - x_min:.1f} x {y_max - y_min:.1f} mm")

        features.append({
            'z': z,
            'x_range': (x_min, x_max),
            'y_range': (y_min, y_max),
            'width': x_max - x_min,
            'height': y_max - y_min
        })

    return features


if __name__ == "__main__":
    import sys
    import warnings
    warnings.filterwarnings('ignore')

    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = "3d-parts/components/power-source-box-schematic.stl"

    results = analyze_stl(filepath)

    # Additional trimesh analysis
    tmesh = analyze_with_trimesh(filepath)

    # Feature detection
    features = find_rectangular_features(filepath)
