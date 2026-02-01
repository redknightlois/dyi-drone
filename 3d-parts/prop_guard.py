"""
Drone Prop Guard - Cage-style protective guard for 2.5" propellers.

Specifications:
- Propeller diameter: 63.5mm (2.5")
- Internal clearance: 5mm each side + wall
- Guard internal diameter: 75mm
- Wall thickness: 3mm
- Outer diameter: 81mm
- Lower ring height: 12mm
- Strut height: 25mm (above lower ring)
- Upper ring height: 4mm
- Total height: 41mm
- 4 struts at 0, 90, 180, 270 degrees
- Clip at 180 degree position, 8mm wide x 12mm long

Geometry notes (for assembly):
- Guard is centered at origin (ring center)
- Clip extends in -X direction (180 degrees)
"""

from build123d import *
from ocp_vscode import show
import math

# Guard dimensions (updated per plan) - exported for assembly.py
PROP_DIAMETER = 63.5    # mm (2.5 inch propeller)
CLEARANCE = 5           # mm safety margin each side
GUARD_ID = 75           # mm internal diameter (63.5 + 5 + 5 + wall adjustment)
GUARD_WALL = 3          # mm wall thickness
GUARD_OD = 81           # mm outer diameter (75 + 3 + 3)

# Ring dimensions
LOWER_RING_HEIGHT = 12  # mm
STRUT_HEIGHT = 25       # mm (above lower ring)
UPPER_RING_HEIGHT = 4   # mm
TOTAL_HEIGHT = 41       # mm (12 + 25 + 4)

# Strut dimensions
STRUT_WIDTH = 4         # mm

# Clip dimensions
CLIP_WIDTH = 8          # mm
CLIP_LENGTH = 12        # mm
CLIP_TAB_WIDTH = 4      # mm (matches arm slot width)
CLIP_TAB_HEIGHT = 8     # mm


def create_prop_guard(verbose=False):
    """Create a cage-style prop guard with upper ring and struts."""

    inner_radius = GUARD_ID / 2
    outer_radius = GUARD_OD / 2
    strut_center_radius = inner_radius + GUARD_WALL / 2

    if verbose:
        print("=" * 50)
        print("PROP GUARD GEOMETRY")
        print("=" * 50)
        print(f"Guard ID: {GUARD_ID} mm, OD: {GUARD_OD} mm")
        print(f"Lower ring height: {LOWER_RING_HEIGHT} mm")
        print(f"Strut height: {STRUT_HEIGHT} mm")
        print(f"Upper ring height: {UPPER_RING_HEIGHT} mm")
        print(f"Total height: {TOTAL_HEIGHT} mm")
        print(f"Clip at: ({-(inner_radius + GUARD_WALL + CLIP_LENGTH/2):.1f}, 0) mm")
        print("=" * 50)

    with BuildPart() as guard:
        # Lower guard ring - base of the cage
        with BuildSketch() as lower_ring:
            Circle(outer_radius)
            Circle(inner_radius, mode=Mode.SUBTRACT)
        extrude(amount=LOWER_RING_HEIGHT)

        # 4 vertical struts extending upward from lower ring
        strut_angles = [0, 90, 180, 270]

        for angle in strut_angles:
            angle_rad = math.radians(angle)
            strut_x = strut_center_radius * math.cos(angle_rad)
            strut_y = strut_center_radius * math.sin(angle_rad)

            with BuildSketch(Plane.XY.offset(LOWER_RING_HEIGHT)) as strut:
                with Locations([(strut_x, strut_y)]):
                    Rectangle(STRUT_WIDTH, STRUT_WIDTH)
            extrude(amount=STRUT_HEIGHT)

        # Upper ring connecting the struts (for blade tip protection)
        upper_ring_z = LOWER_RING_HEIGHT + STRUT_HEIGHT
        with BuildSketch(Plane.XY.offset(upper_ring_z)) as upper_ring:
            Circle(outer_radius)
            Circle(inner_radius, mode=Mode.SUBTRACT)
        extrude(amount=UPPER_RING_HEIGHT)

        # Mounting clip (at 180 degree position, pointing outward)
        clip_x = -(inner_radius + GUARD_WALL + CLIP_LENGTH/2)
        with BuildSketch(Plane.XY) as clip_base:
            with Locations([(clip_x, 0)]):
                RectangleRounded(CLIP_LENGTH, CLIP_WIDTH, radius=1)
        extrude(amount=LOWER_RING_HEIGHT - 2)

        # Clip tab (the part that snaps into arm slot)
        tab_x = -(inner_radius + GUARD_WALL + CLIP_LENGTH - 3)
        with BuildSketch(Plane.XY.offset(LOWER_RING_HEIGHT/2 - CLIP_TAB_HEIGHT/2)) as tab:
            with Locations([(tab_x, 0)]):
                Rectangle(4, CLIP_TAB_WIDTH - 0.4)  # Slightly smaller for snap fit
        extrude(amount=CLIP_TAB_HEIGHT)

        # Flexibility slot in clip for snap action
        flex_slot_x = -(inner_radius + GUARD_WALL + CLIP_LENGTH/2)
        with BuildSketch(Plane.XZ.offset(0)) as flex_slot:
            with Locations([(flex_slot_x, LOWER_RING_HEIGHT/2)]):
                Rectangle(CLIP_LENGTH - 4, 2)
        extrude(amount=1.5, both=True, mode=Mode.SUBTRACT)

    return guard.part


# Create the prop guard
guard = create_prop_guard()

if __name__ == "__main__":
    show(guard)
