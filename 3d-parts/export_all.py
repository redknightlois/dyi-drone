"""
Export script for drone frame 3D parts.

Generates:
- STL files for 3D printing
- GLTF/GLB files for web viewing
- HTML viewer with model-viewer component

Usage: python 3d-parts/export_all.py
"""

import sys
from pathlib import Path

# Add the 3d-parts directory to path for imports
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from build123d import *

# Import part creation functions
from frame_body import create_body
from frame_arm import create_arm
from prop_guard import create_prop_guard
from battery_cover import create_battery_cover
from assembly import create_assembly

# Export directory - use project root /build folder
PROJECT_ROOT = script_dir.parent
EXPORT_DIR = PROJECT_ROOT / "build"
EXPORT_DIR.mkdir(exist_ok=True)


def export_stl_file(part, filename):
    """Export a part to STL format."""
    filepath = EXPORT_DIR / filename
    export_stl(part, str(filepath))
    print(f"  Exported: {filepath}")


def export_step_file(part, filename):
    """Export a part to STEP format."""
    filepath = EXPORT_DIR / filename
    export_step(part, str(filepath))
    print(f"  Exported: {filepath}")


def export_gltf_file(part, filename):
    """Export a part to GLTF format."""
    filepath = EXPORT_DIR / filename
    try:
        export_gltf(part, str(filepath))
        print(f"  Exported: {filepath}")
    except Exception as e:
        print(f"  Warning: GLTF export failed for {filename}: {e}")
        print(f"  Trying alternative export method...")
        # Try exporting as STL and note for manual conversion
        stl_path = filepath.with_suffix('.stl')
        export_stl(part, str(stl_path))
        print(f"  Exported STL instead: {stl_path}")


def generate_viewer_html():
    """Generate an HTML viewer using model-viewer."""
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Drone Frame 3D Viewer</title>
    <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }
        .header {
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .header h1 {
            font-size: 24px;
            font-weight: 600;
        }
        .header p {
            color: rgba(255,255,255,0.6);
            margin-top: 5px;
        }
        .container {
            display: flex;
            height: calc(100vh - 100px);
        }
        .viewer-panel {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        model-viewer {
            width: 100%;
            height: 100%;
            min-height: 500px;
            background: radial-gradient(circle at center, #2a2a4a 0%, #1a1a2e 100%);
            border-radius: 12px;
            --poster-color: transparent;
        }
        .sidebar {
            width: 280px;
            background: rgba(255,255,255,0.05);
            padding: 20px;
            overflow-y: auto;
        }
        .part-card {
            background: rgba(255,255,255,0.08);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 12px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .part-card:hover {
            background: rgba(255,255,255,0.12);
            transform: translateX(5px);
        }
        .part-card.active {
            background: rgba(74, 144, 226, 0.3);
            border: 1px solid rgba(74, 144, 226, 0.5);
        }
        .part-card h3 {
            font-size: 14px;
            margin-bottom: 5px;
        }
        .part-card p {
            font-size: 12px;
            color: rgba(255,255,255,0.6);
        }
        .part-card .qty {
            display: inline-block;
            background: rgba(74, 144, 226, 0.3);
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            margin-top: 8px;
        }
        .section-title {
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: rgba(255,255,255,0.4);
            margin-bottom: 15px;
        }
        .download-btn {
            display: block;
            width: 100%;
            padding: 12px;
            background: #4a90e2;
            border: none;
            border-radius: 8px;
            color: white;
            font-size: 14px;
            cursor: pointer;
            margin-top: 10px;
            text-decoration: none;
            text-align: center;
            transition: background 0.2s;
        }
        .download-btn:hover {
            background: #357abd;
        }
        .specs {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        .spec-row {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            padding: 5px 0;
        }
        .spec-row .label {
            color: rgba(255,255,255,0.6);
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Drone Frame 3D Viewer</h1>
        <p>Interactive preview of printable drone parts</p>
    </div>

    <div class="container">
        <div class="viewer-panel">
            <model-viewer
                id="viewer"
                src="drone_assembly.glb"
                alt="Drone Frame Assembly"
                camera-controls
                auto-rotate
                shadow-intensity="1"
                environment-image="neutral"
                exposure="0.8"
                camera-orbit="45deg 55deg 300mm"
                min-camera-orbit="auto auto 100mm"
                max-camera-orbit="auto auto 500mm"
            >
            </model-viewer>
        </div>

        <div class="sidebar">
            <div class="section-title">Parts</div>

            <div class="part-card active" onclick="loadModel('drone_assembly.glb', this)">
                <h3>Complete Assembly</h3>
                <p>Full drone frame with all parts</p>
                <span class="qty">Preview Only</span>
            </div>

            <div class="part-card" onclick="loadModel('frame_body.glb', this)">
                <h3>Frame Body</h3>
                <p>Central body with Arduino & IMU mounts</p>
                <span class="qty">x1</span>
                <a href="frame_body.stl" class="download-btn" onclick="event.stopPropagation()">Download STL</a>
            </div>

            <div class="part-card" onclick="loadModel('frame_arm.glb', this)">
                <h3>Frame Arm</h3>
                <p>Motor mount arm with I-beam profile</p>
                <span class="qty">x4</span>
                <a href="frame_arm.stl" class="download-btn" onclick="event.stopPropagation()">Download STL</a>
            </div>

            <div class="part-card" onclick="loadModel('prop_guard.glb', this)">
                <h3>Prop Guard</h3>
                <p>2.5" propeller protection ring</p>
                <span class="qty">x4</span>
                <a href="prop_guard.stl" class="download-btn" onclick="event.stopPropagation()">Download STL</a>
            </div>

            <div class="part-card" onclick="loadModel('battery_cover.glb', this)">
                <h3>Battery Cover</h3>
                <p>LiPo 2S protective cover</p>
                <span class="qty">x1</span>
                <a href="battery_cover.stl" class="download-btn" onclick="event.stopPropagation()">Download STL</a>
            </div>

            <div class="specs">
                <div class="section-title">Specifications</div>
                <div class="spec-row">
                    <span class="label">Propellers</span>
                    <span>2.5" (63.5mm)</span>
                </div>
                <div class="spec-row">
                    <span class="label">Motors</span>
                    <span>820 Brushed</span>
                </div>
                <div class="spec-row">
                    <span class="label">Battery</span>
                    <span>LiPo 2S</span>
                </div>
                <div class="spec-row">
                    <span class="label">Controller</span>
                    <span>Arduino R4 WiFi</span>
                </div>
                <div class="spec-row">
                    <span class="label">IMU</span>
                    <span>MPU6050</span>
                </div>
                <div class="spec-row">
                    <span class="label">Print Bed</span>
                    <span>220x220mm</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        function loadModel(filename, element) {
            document.getElementById('viewer').src = filename;
            document.querySelectorAll('.part-card').forEach(card => card.classList.remove('active'));
            element.classList.add('active');
        }
    </script>
</body>
</html>
'''
    filepath = EXPORT_DIR / "viewer.html"
    filepath.write_text(html_content, encoding='utf-8')
    print(f"  Generated: {filepath}")


def main():
    """Main export function."""
    print("=" * 50)
    print("Drone Frame 3D Parts Export")
    print("=" * 50)

    print("\nCreating parts...")

    # Create all parts
    print("  Creating frame body...")
    body = create_body()

    print("  Creating frame arm...")
    arm = create_arm()

    print("  Creating prop guard...")
    guard = create_prop_guard()

    print("  Creating battery cover...")
    cover = create_battery_cover()

    print("  Creating assembly...")
    body_parts, arm_parts, guard_parts, cover_parts = create_assembly()

    # Combine all assembly parts into a single compound for export
    with BuildPart() as assembly_builder:
        for part in body_parts:
            add(part)
        for part in arm_parts:
            add(part)
        for part in guard_parts:
            add(part)
        for part in cover_parts:
            add(part)
    assembly = assembly_builder.part

    # Export STL files (for 3D printing)
    print("\nExporting STL files (for 3D printing)...")
    export_stl_file(body, "frame_body.stl")
    export_stl_file(arm, "frame_arm.stl")
    export_stl_file(guard, "prop_guard.stl")
    export_stl_file(cover, "battery_cover.stl")
    export_stl_file(assembly, "drone_assembly.stl")

    # Export STEP files (for CAD import)
    print("\nExporting STEP files (for CAD)...")
    export_step_file(body, "frame_body.step")
    export_step_file(arm, "frame_arm.step")
    export_step_file(guard, "prop_guard.step")
    export_step_file(cover, "battery_cover.step")
    export_step_file(assembly, "drone_assembly.step")

    # Export GLTF files (for web viewer)
    print("\nExporting GLTF files (for web viewer)...")
    export_gltf_file(body, "frame_body.glb")
    export_gltf_file(arm, "frame_arm.glb")
    export_gltf_file(guard, "prop_guard.glb")
    export_gltf_file(cover, "battery_cover.glb")
    export_gltf_file(assembly, "drone_assembly.glb")

    # Generate HTML viewer
    print("\nGenerating HTML viewer...")
    generate_viewer_html()

    # Export PNG images
    print("\nExporting PNG images...")
    try:
        from render_images import render_part, render_assembly

        # Individual parts (isometric view)
        render_part(body, EXPORT_DIR / "frame_body.png", color='#505050')
        render_part(arm, EXPORT_DIR / "frame_arm.png", color='#4682B4')
        render_part(guard, EXPORT_DIR / "prop_guard.png", color='#FF6600')
        render_part(cover, EXPORT_DIR / "battery_cover.png", color='#228B22')

        # Assembly views with colors
        assembly_parts = [
            (body_parts, '#505050'),    # Dark gray
            (arm_parts, '#4682B4'),     # Steel blue
            (guard_parts, '#FF6600'),   # Orange
            (cover_parts, '#228B22'),   # Forest green
        ]

        for view in ['iso', 'top', 'left', 'right']:
            render_assembly(
                assembly_parts,
                EXPORT_DIR / f"drone_assembly_{view}.png",
                camera=view
            )

        print("  PNG export complete!")
    except ImportError as e:
        print(f"  Warning: PNG export skipped - PyVista not available: {e}")
    except Exception as e:
        print(f"  Warning: PNG export failed: {e}")

    print("\n" + "=" * 50)
    print("Export complete!")
    print(f"Files saved to: {EXPORT_DIR}")
    print("\nTo view in browser, open:")
    print(f"  {EXPORT_DIR / 'viewer.html'}")
    print("=" * 50)


if __name__ == "__main__":
    main()
