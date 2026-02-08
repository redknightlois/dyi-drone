"""
Drone Battery Cover - Protective cover for LiPo 2S battery.

Specifications:
- Base size: 60 x 40 x 2 mm
- Wall height: 6mm
- Fits 55 x 30 mm battery compartment from frame body
- Rail slots: 4mm wide (matches frame rails)
- Honeycomb ventilation: 5mm cells, 1.5mm walls
- Finger grip: 8mm radius semicircle cutout
"""

from build123d import *
from ocp_vscode import show, set_defaults
import math

# Cover dimensions (updated per plan)
COVER_LENGTH = 60       # mm
COVER_WIDTH = 40        # mm
COVER_THICKNESS = 2     # mm base plate
WALL_HEIGHT = 6         # mm

# Battery compartment from frame body
BATTERY_COMP_LENGTH = 55  # mm
BATTERY_COMP_WIDTH = 30   # mm

# Rail dimensions (to slide onto frame rails)
RAIL_SLOT_WIDTH = 4.5   # mm (slightly larger than 4mm frame rails for clearance)
RAIL_SLOT_DEPTH = 6     # mm
RAIL_SPACING = 38       # mm between rail centers (matching frame body rail positions at ±19mm)

# Finger grip
GRIP_RADIUS = 8         # mm


def create_honeycomb_pattern(length, width, cell_size=5, wall=1.5):
    """Create a honeycomb pattern of hexagonal cutouts."""
    holes = []

    hex_width = cell_size * math.sqrt(3)
    x_spacing = hex_width + wall
    y_spacing = (cell_size * 1.5) + wall * 0.866

    cols = int(length / x_spacing) + 1
    rows = int(width / y_spacing) + 1

    x_offset = -(cols - 1) * x_spacing / 2
    y_offset = -(rows - 1) * y_spacing / 2

    for row in range(rows):
        for col in range(cols):
            x = x_offset + col * x_spacing
            if row % 2 == 1:
                x += x_spacing / 2
            y = y_offset + row * y_spacing

            if abs(x) < length/2 - cell_size * 0.8 and abs(y) < width/2 - cell_size * 0.8:
                holes.append((x, y))

    return holes, cell_size * 0.8


def create_battery_cover(verbose=False):
    """Create a battery cover with honeycomb ventilation."""

    if verbose:
        print("=" * 50)
        print("BATTERY COVER GEOMETRY")
        print("=" * 50)
        print(f"Cover size: {COVER_LENGTH} x {COVER_WIDTH} x {COVER_THICKNESS} mm")
        print(f"Wall height: {WALL_HEIGHT} mm")
        print(f"Rail spacing: {RAIL_SPACING} mm")
        print(f"Fits battery compartment: {BATTERY_COMP_LENGTH} x {BATTERY_COMP_WIDTH} mm")
        print("=" * 50)

    with BuildPart() as cover:
        # Main cover plate
        with BuildSketch() as base:
            RectangleRounded(COVER_LENGTH, COVER_WIDTH, radius=4)
        extrude(amount=COVER_THICKNESS)

        # Side walls (perimeter frame)
        wall_thickness = 3
        with BuildSketch(Plane.XY.offset(COVER_THICKNESS)) as walls:
            # Outer boundary
            RectangleRounded(COVER_LENGTH, COVER_WIDTH, radius=4)
            # Inner cutout (hollow)
            with Locations([(0, 0)]):
                RectangleRounded(
                    COVER_LENGTH - wall_thickness * 2,
                    COVER_WIDTH - wall_thickness * 2,
                    radius=2,
                    mode=Mode.SUBTRACT
                )
        extrude(amount=WALL_HEIGHT)

        # Rail guide channels on the sides (slide onto frame rails)
        rail_y = RAIL_SPACING / 2
        for side in [1, -1]:
            # Create rail channel slot
            with BuildSketch(Plane.XY.offset(COVER_THICKNESS)) as rail_guide:
                with Locations([(0, side * rail_y)]):
                    Rectangle(COVER_LENGTH - 10, RAIL_SLOT_WIDTH)
            extrude(amount=WALL_HEIGHT, mode=Mode.SUBTRACT)

        # Honeycomb ventilation pattern on base
        hex_positions, hex_radius = create_honeycomb_pattern(
            COVER_LENGTH - 15, COVER_WIDTH - 15, cell_size=5, wall=1.5
        )

        if hex_positions:
            with BuildSketch(Plane.XY.offset(COVER_THICKNESS)) as honeycomb:
                for hx, hy in hex_positions:
                    # Skip positions in rail areas
                    if abs(hy) < RAIL_SPACING/2 - 3:
                        with Locations([(hx, hy)]):
                            RegularPolygon(radius=hex_radius, side_count=6)
            extrude(amount=-COVER_THICKNESS, mode=Mode.SUBTRACT)

        # Finger grip cutout at front for easy removal (semicircle)
        with BuildSketch(Plane.XZ.offset(0)) as grip:
            with Locations([(COVER_LENGTH/2 - 2, COVER_THICKNESS/2)]):
                Circle(GRIP_RADIUS)
        extrude(amount=15, both=True, mode=Mode.SUBTRACT)

        # Rear tab for secure fit (prevents cover from sliding out)
        with BuildSketch(Plane.XY.offset(COVER_THICKNESS)) as rear_tab:
            with Locations([(-COVER_LENGTH/2 + 5, 0)]):
                RectangleRounded(8, 20, radius=2)
        extrude(amount=3)

    return cover.part


# Create the battery cover
cover = create_battery_cover()

if __name__ == "__main__":
    set_defaults(axes=True, axes0=True, grid=[True, False, False])
    show(cover)
