# Build123d Skills

## Overview

Build123d is a Python library for creating 3D CAD models programmatically. This project uses it to design the drone frame parts.

## Installation

```bash
pip install build123d ocp-vscode pyvista
```

For visualization in VS Code, install the OCP CAD Viewer extension.

PyVista is required for PNG image rendering.

## Regenerate Exports

To regenerate all STL, STEP, GLTF files and the HTML viewer:

```bash
cd D:\Src\drone
python 3d-parts/export_all.py
```

## View in Browser

After exporting, open the 3D viewer:

```bash
# Windows
start 3d-parts/exports/viewer.html

# Or just open in browser
# D:\Src\drone\3d-parts\exports\viewer.html
```

## Preview Individual Parts

With OCP Viewer extension in VS Code:

```bash
# Open any part file and run it
python 3d-parts/frame_body.py
python 3d-parts/frame_arm.py
python 3d-parts/prop_guard.py
python 3d-parts/battery_cover.py
python 3d-parts/assembly.py
```

## Output Files

| File | Purpose |
|------|---------|
| `exports/frame_body.stl` | Body for 3D printing |
| `exports/frame_arm.stl` | Arm for 3D printing (x4) |
| `exports/prop_guard.stl` | Guard for 3D printing (x4) |
| `exports/battery_cover.stl` | Cover for 3D printing |
| `exports/drone_assembly.stl` | Full assembly STL |
| `exports/*.step` | STEP files for CAD software |
| `exports/*.glb` | GLTF files for web viewer |
| `exports/viewer.html` | Interactive 3D viewer |
| `exports/*.png` | Static rendered images |

### PNG Images

Individual parts (isometric view):

| File | Color |
|------|-------|
| `frame_body.png` | Dark gray (#505050) |
| `frame_arm.png` | Steel blue (#4682B4) |
| `prop_guard.png` | Orange (#FF6600) |
| `battery_cover.png` | Forest green (#228B22) |

Assembly views (multiple angles):

| File | Camera Angle |
|------|--------------|
| `drone_assembly_iso.png` | Isometric |
| `drone_assembly_top.png` | Top-down |
| `drone_assembly_left.png` | Left side |
| `drone_assembly_right.png` | Right side |

## Modifying Parts

Each part file (`frame_body.py`, etc.) contains:

1. Constants at the top for dimensions
2. A `create_*()` function that builds the part
3. A `show()` call for previewing

To modify a part:

1. Edit the constants or geometry
2. Run the file to preview: `python 3d-parts/frame_body.py`
3. Regenerate exports: `python 3d-parts/export_all.py`

## Common Operations

### Change motor size

Edit `frame_arm.py`:
```python
MOTOR_DIAMETER = 8.0  # Change this value
MOTOR_LENGTH = 20.0   # Change this value
```

### Change propeller size

Edit `prop_guard.py`:
```python
PROP_DIAMETER = 63.5  # 2.5" = 63.5mm
CLEARANCE = 5         # Safety margin
GUARD_ID = 75         # Internal diameter
```

### Change Arduino mount

Edit `frame_body.py`:
```python
ARDUINO_LENGTH = 68.5  # mm
ARDUINO_WIDTH = 53.4   # mm
```

## Rendering Images

The `render_images.py` module provides PyVista-based rendering for static PNG output.

### Render a single part

```python
from render_images import render_part
from frame_body import create_body

body = create_body()
render_part(body, "my_body.png", camera='iso', color='#505050')
```

### Render assembly with colors

```python
from render_images import render_assembly
from assembly import create_assembly

body_parts, arm_parts, guard_parts, cover_parts = create_assembly()

assembly_parts = [
    (body_parts, '#505050'),    # Dark gray
    (arm_parts, '#4682B4'),     # Steel blue
    (guard_parts, '#FF6600'),   # Orange
    (cover_parts, '#228B22'),   # Forest green
]

render_assembly(assembly_parts, "assembly.png", camera='top')
```

### Camera presets

| Preset | Description |
|--------|-------------|
| `iso` | Classic isometric view (default) |
| `top` | Top-down, looking at XY plane |
| `front` | Front view, looking at XZ plane |
| `left` | Left side view |
| `right` | Right side view |
| `rear` | Rear view |

### Custom render settings

```python
render_part(
    part,
    "output.png",
    camera='iso',           # Camera preset
    color='#4682B4',        # Hex color
    size=(1024, 768),       # Image dimensions (default: 800x600)
    background='#F5F5F5'    # Background color (default: light gray)
)
```

## Troubleshooting

### GLTF export fails

If GLTF export fails, STL files will still be generated. You can convert STL to GLTF using online tools or Blender.

### Part doesn't render

Make sure OCP Viewer extension is installed and running in VS Code.

### Dimensions don't match

All dimensions are in millimeters. Verify your slicer is set to mm units when importing STL files.

### PNG rendering fails

If PyVista is not installed or fails:

```bash
pip install pyvista
```

PNG export will be skipped if PyVista is unavailable. Other exports (STL, STEP, GLTF) will still work.

### Images are black or empty

Ensure the part has valid geometry. Try rendering with a different camera preset if the view angle is problematic.
