"""
STL Validation Script - Compares generated STL files against reference meshes.

Uses Hausdorff distance and volume comparison to validate that generated
parts match the reference schematics within acceptable tolerances.

Usage: python 3d-parts/validate_stl.py
"""

import sys
from pathlib import Path

try:
    import trimesh
    import numpy as np
    from scipy.spatial.distance import directed_hausdorff
except ImportError as e:
    print(f"Error: Required package not installed: {e}")
    print("Install with: pip install trimesh scipy numpy")
    sys.exit(1)


# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
BUILD_DIR = PROJECT_ROOT / "build"
COMPONENTS_DIR = SCRIPT_DIR / "components"


# Validation thresholds
HAUSDORFF_THRESHOLD_MM = 1.0  # Maximum acceptable Hausdorff distance
VOLUME_DIFF_THRESHOLD_PCT = 5.0  # Maximum acceptable volume difference


def load_mesh(filepath: Path) -> trimesh.Trimesh:
    """Load an STL file as a trimesh object."""
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    return trimesh.load(filepath)


def compute_hausdorff_distance(mesh1: trimesh.Trimesh, mesh2: trimesh.Trimesh,
                                num_samples: int = 10000) -> dict:
    """
    Compute Hausdorff distance between two meshes.

    Samples points from both mesh surfaces and computes the maximum
    minimum distance in both directions.

    Args:
        mesh1: First mesh (generated)
        mesh2: Second mesh (reference)
        num_samples: Number of points to sample from each surface

    Returns:
        Dictionary with hausdorff distances and statistics
    """
    # Sample points from mesh surfaces
    pts1, _ = trimesh.sample.sample_surface(mesh1, num_samples)
    pts2, _ = trimesh.sample.sample_surface(mesh2, num_samples)

    # Compute directed Hausdorff distances
    d1, _, _ = directed_hausdorff(pts1, pts2)
    d2, _, _ = directed_hausdorff(pts2, pts1)

    # Symmetric Hausdorff distance is the maximum of both directions
    hausdorff = max(d1, d2)

    return {
        'hausdorff': hausdorff,
        'hausdorff_gen_to_ref': d1,
        'hausdorff_ref_to_gen': d2,
    }


def compute_volume_difference(mesh1: trimesh.Trimesh, mesh2: trimesh.Trimesh) -> dict:
    """
    Compute volume difference between two meshes.

    Args:
        mesh1: First mesh (generated)
        mesh2: Second mesh (reference)

    Returns:
        Dictionary with volume comparison statistics
    """
    vol1 = abs(mesh1.volume)
    vol2 = abs(mesh2.volume)

    diff_abs = abs(vol1 - vol2)
    diff_pct = (diff_abs / vol2) * 100 if vol2 > 0 else float('inf')

    return {
        'volume_generated': vol1,
        'volume_reference': vol2,
        'volume_diff_abs': diff_abs,
        'volume_diff_pct': diff_pct,
    }


def validate_mesh(gen_path: Path, ref_path: Path, name: str) -> dict:
    """
    Validate a generated mesh against a reference mesh.

    Args:
        gen_path: Path to generated STL file
        ref_path: Path to reference STL file
        name: Name of the part for reporting

    Returns:
        Dictionary with validation results
    """
    print(f"\n{'='*60}")
    print(f"Validating: {name}")
    print(f"{'='*60}")
    print(f"  Generated: {gen_path}")
    print(f"  Reference: {ref_path}")

    result = {
        'name': name,
        'generated_path': str(gen_path),
        'reference_path': str(ref_path),
        'passed': False,
        'errors': [],
    }

    # Load meshes
    try:
        gen_mesh = load_mesh(gen_path)
        print(f"  Generated mesh loaded: {len(gen_mesh.vertices)} vertices, {len(gen_mesh.faces)} faces")
    except FileNotFoundError as e:
        result['errors'].append(f"Generated file not found: {gen_path}")
        print(f"  ERROR: {result['errors'][-1]}")
        return result

    try:
        ref_mesh = load_mesh(ref_path)
        print(f"  Reference mesh loaded: {len(ref_mesh.vertices)} vertices, {len(ref_mesh.faces)} faces")
    except FileNotFoundError as e:
        result['errors'].append(f"Reference file not found: {ref_path}")
        print(f"  ERROR: {result['errors'][-1]}")
        return result

    # Compute Hausdorff distance
    print("\n  Computing Hausdorff distance...")
    hausdorff_result = compute_hausdorff_distance(gen_mesh, ref_mesh)
    result.update(hausdorff_result)

    hausdorff = hausdorff_result['hausdorff']
    print(f"    Hausdorff distance: {hausdorff:.3f} mm")
    print(f"    (gen->ref: {hausdorff_result['hausdorff_gen_to_ref']:.3f} mm, "
          f"ref->gen: {hausdorff_result['hausdorff_ref_to_gen']:.3f} mm)")

    if hausdorff > HAUSDORFF_THRESHOLD_MM:
        result['errors'].append(
            f"Hausdorff distance {hausdorff:.3f} mm exceeds threshold {HAUSDORFF_THRESHOLD_MM} mm"
        )
        print(f"    FAIL: {result['errors'][-1]}")
    else:
        print(f"    PASS: Within threshold ({HAUSDORFF_THRESHOLD_MM} mm)")

    # Compute volume difference
    print("\n  Computing volume difference...")
    volume_result = compute_volume_difference(gen_mesh, ref_mesh)
    result.update(volume_result)

    vol_diff_pct = volume_result['volume_diff_pct']
    print(f"    Generated volume: {volume_result['volume_generated']:.2f} mm³")
    print(f"    Reference volume: {volume_result['volume_reference']:.2f} mm³")
    print(f"    Difference: {volume_result['volume_diff_abs']:.2f} mm³ ({vol_diff_pct:.2f}%)")

    if vol_diff_pct > VOLUME_DIFF_THRESHOLD_PCT:
        result['errors'].append(
            f"Volume difference {vol_diff_pct:.2f}% exceeds threshold {VOLUME_DIFF_THRESHOLD_PCT}%"
        )
        print(f"    FAIL: {result['errors'][-1]}")
    else:
        print(f"    PASS: Within threshold ({VOLUME_DIFF_THRESHOLD_PCT}%)")

    # Overall result
    result['passed'] = len(result['errors']) == 0
    status = "PASSED" if result['passed'] else "FAILED"
    print(f"\n  Overall: {status}")

    return result


def main():
    """Run validation on all power source box parts."""
    print("=" * 60)
    print("STL Validation - Power Source Box")
    print("=" * 60)
    print(f"Hausdorff threshold: {HAUSDORFF_THRESHOLD_MM} mm")
    print(f"Volume diff threshold: {VOLUME_DIFF_THRESHOLD_PCT}%")

    # Parts to validate: (name, generated_filename, reference_filename)
    parts = [
        ("Power Source Lid", "power_source_lid.stl", "power-source-box-schematic.stl"),
        ("Power Source Case", "power_source_case.stl", "power-source-box-schematic_mount.stl"),
        ("Mounting Pin", "power_source_pin.stl", "power-source-box-schematic_pin.stl"),
    ]

    results = []
    for name, gen_file, ref_file in parts:
        gen_path = BUILD_DIR / gen_file
        ref_path = COMPONENTS_DIR / ref_file
        result = validate_mesh(gen_path, ref_path, name)
        results.append(result)

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    passed = sum(1 for r in results if r['passed'])
    failed = len(results) - passed

    for r in results:
        status = "PASS" if r['passed'] else "FAIL"
        hausdorff = r.get('hausdorff', float('nan'))
        vol_diff = r.get('volume_diff_pct', float('nan'))
        print(f"  [{status}] {r['name']}: "
              f"Hausdorff={hausdorff:.3f}mm, VolDiff={vol_diff:.2f}%")

    print(f"\nTotal: {passed}/{len(results)} passed")

    if failed > 0:
        print("\nFailed validations:")
        for r in results:
            if not r['passed']:
                print(f"  {r['name']}:")
                for err in r['errors']:
                    print(f"    - {err}")
        sys.exit(1)
    else:
        print("\nAll validations passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
