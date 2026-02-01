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
- Central friction-fit sleeve for motor mount attachment

Geometry notes (for assembly):
- Guard is centered at origin (ring center = motor center)
- Central sleeve slides over the motor mount cylinder
- Friction fit holds guard in place
"""

from build123d import *
from ocp_vscode import show
import math

# Guard dimensions - exported for assembly.py
PROP_DIAMETER = 63.5    # mm (2.5 inch propeller)
CLEARANCE = 5           # mm safety margin each side
GUARD_ID = 75           # mm internal diameter
GUARD_WALL = 3          # mm wall thickness
GUARD_OD = 81           # mm outer diameter (75 + 3 + 3)

# Ring dimensions
LOWER_RING_HEIGHT = 12  # mm
STRUT_HEIGHT = 25       # mm (above lower ring)
UPPER_RING_HEIGHT = 4   # mm
TOTAL_HEIGHT = 41       # mm (12 + 25 + 4)

# Strut dimensions
STRUT_WIDTH = 4         # mm

# Central sleeve for friction fit (must match frame_arm.py motor mount)
MOTOR_MOUNT_OD = 12     # mm - from frame_arm.py
SLEEVE_ID = 12.3        # mm - slight clearance for friction fit
SLEEVE_OD = 16          # mm - wall thickness for strength
SLEEVE_HEIGHT = 10      # mm - enough grip length

# No strut extension needed with friction fit
STRUT_EXTENSION = 0     # mm - exported for assembly.py compatibility


def create_prop_guard(verbose=False):
    """Create a cage-style prop guard with central friction-fit sleeve."""

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
        print(f"Sleeve ID: {SLEEVE_ID} mm (fits over {MOTOR_MOUNT_OD} mm motor mount)")
        print(f"Sleeve height: {SLEEVE_HEIGHT} mm")
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

            # Main strut going up
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

        # Central friction-fit sleeve - slides over motor mount
        # Extends downward from center of lower ring
        with BuildSketch(Plane.XY) as sleeve:
            Circle(SLEEVE_OD / 2)
            Circle(SLEEVE_ID / 2, mode=Mode.SUBTRACT)
        extrude(amount=-SLEEVE_HEIGHT)

        # Add connecting spokes from sleeve to lower ring (4 spokes)
        spoke_angles = [45, 135, 225, 315]  # Between the struts
        for angle in spoke_angles:
            angle_rad = math.radians(angle)

            # Spoke connects sleeve OD to ring ID
            spoke_length = inner_radius - SLEEVE_OD / 2
            spoke_center_radius = SLEEVE_OD / 2 + spoke_length / 2
            spoke_x = spoke_center_radius * math.cos(angle_rad)
            spoke_y = spoke_center_radius * math.sin(angle_rad)

            with BuildSketch(Plane.XY) as spoke:
                with Locations([(spoke_x, spoke_y)]):
                    Rectangle(spoke_length, 3, rotation=angle)
            extrude(amount=3)  # Thin spoke at bottom of ring

    return guard.part


# Create the prop guard
guard = create_prop_guard()

if __name__ == "__main__":
    show(guard)
