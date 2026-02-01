"""
Drone Frame Body - Central body with Arduino mount, IMU center mount, and battery compartment.

Specifications:
- Dimensions: 95 x 75 x 4 mm (base plate)
- Arduino R4 WiFi mounting (68.5 x 53.4 mm, holes at 66 x 48 mm spacing)
- MPU6050 IMU mount at geometric center (25 x 20 mm platform)
- LiPo 2S battery compartment (55 x 30 mm centered below)
- 4 arm mounting points at 45 degrees, 40mm from center
- Triangular truss pattern for weight reduction (stronger than honeycomb)
"""

from build123d import *
from ocp_vscode import show
import math

# Body dimensions (updated per plan)
BODY_LENGTH = 95  # mm
BODY_WIDTH = 75   # mm
BODY_THICKNESS = 4  # mm
WALL_THICKNESS = 2  # mm

# Arduino R4 WiFi dimensions
ARDUINO_HOLE_SPACING_L = 66.0  # mm
ARDUINO_HOLE_SPACING_W = 48.0  # mm
STANDOFF_HEIGHT = 8  # mm
STANDOFF_OD = 6  # mm
STANDOFF_ID = 3.2  # mm (M3 clearance)

# IMU MPU6050 dimensions
IMU_PLATFORM_L = 25  # mm
IMU_PLATFORM_W = 20  # mm
IMU_PLATFORM_HEIGHT = 2  # mm (raised from base)
IMU_HOLE_SPACING = 15.24  # mm (0.6 inches square)
IMU_HOLE_DIA = 2.6  # mm (M2.5 clearance)

# Battery compartment
BATTERY_COMP_LENGTH = 55  # mm
BATTERY_COMP_WIDTH = 30   # mm
BATTERY_RAIL_HEIGHT = 6   # mm (extends below base)
BATTERY_RAIL_WIDTH = 4    # mm

# Arm mounting (updated per plan)
ARM_MOUNT_DISTANCE = 40  # mm from center (diagonal)
ARM_MOUNT_WIDTH = 14  # mm
ARM_MOUNT_LENGTH = 18  # mm
ARM_MOUNT_HOLE_DIA = 3.2  # mm (M3 clearance)
ARM_MOUNT_HOLE_SPACING = 10  # mm between holes

# Triangular truss pattern (stronger than honeycomb)
TRUSS_HOLE_SIZE = 10  # mm triangle side
TRUSS_WALL = 3        # mm wall thickness (increased for strength)


def create_triangular_pattern(length, width, tri_size=10, wall=3):
    """Create a triangular truss pattern of cutouts - stronger than honeycomb."""
    triangles = []  # List of (x, y, pointing_up)

    # Triangle geometry
    tri_height = tri_size * math.sqrt(3) / 2

    # Spacing
    x_spacing = tri_size + wall
    y_spacing = tri_height + wall * 0.866

    # Calculate grid
    cols = int(length / x_spacing)
    rows = int(width / y_spacing)

    # Center the pattern
    x_offset = -(cols - 1) * x_spacing / 2
    y_offset = -(rows - 1) * y_spacing / 2

    for row in range(rows):
        for col in range(cols):
            x = x_offset + col * x_spacing
            # Offset alternating rows
            if row % 2 == 1:
                x += x_spacing / 2
            y = y_offset + row * y_spacing

            # Alternate triangle direction
            pointing_up = (row + col) % 2 == 0

            # Only include if within bounds
            if abs(x) < length/2 - tri_size * 0.6 and abs(y) < width/2 - tri_size * 0.6:
                triangles.append((x, y, pointing_up))

    return triangles, tri_size * 0.4  # Return positions and effective radius


def create_body():
    """Create the main drone body."""

    # Print position info
    print("=" * 60)
    print("FRAME BODY POSITIONS")
    print("=" * 60)
    print(f"Body dimensions: {BODY_LENGTH} x {BODY_WIDTH} x {BODY_THICKNESS} mm")
    print(f"Body center: (0, 0, 0)")
    print(f"Body top surface: Z = {BODY_THICKNESS} mm")
    print()

    with BuildPart() as body:
        # Main platform - rounded rectangle
        with BuildSketch() as base:
            RectangleRounded(BODY_LENGTH, BODY_WIDTH, radius=8)
        extrude(amount=BODY_THICKNESS)

        # Arm mounting extensions at 45 degree positions
        arm_angles = [45, 135, 225, 315]
        arm_names = ["Front-Right", "Front-Left", "Rear-Left", "Rear-Right"]

        print("Arm Mount Positions (on body):")
        for i, angle in enumerate(arm_angles):
            angle_rad = math.radians(angle)
            x = ARM_MOUNT_DISTANCE * math.cos(angle_rad)
            y = ARM_MOUNT_DISTANCE * math.sin(angle_rad)
            print(f"  {arm_names[i]} ({angle}°): ({x:.1f}, {y:.1f}) mm, Z = {BODY_THICKNESS}-{BODY_THICKNESS + 4} mm")

            with BuildSketch(Plane.XY.offset(BODY_THICKNESS)) as arm_mount:
                with Locations([(x, y)]):
                    RectangleRounded(ARM_MOUNT_LENGTH, ARM_MOUNT_WIDTH, radius=2, rotation=angle)
            extrude(amount=4)

            # Arm mounting holes (along the arm direction)
            hole_offset = ARM_MOUNT_HOLE_SPACING / 2
            for dx in [-hole_offset, hole_offset]:
                hx = x + dx * math.cos(angle_rad)
                hy = y + dx * math.sin(angle_rad)
                Hole(ARM_MOUNT_HOLE_DIA/2, depth=BODY_THICKNESS + 4).locate(
                    Location((hx, hy, BODY_THICKNESS + 4))
                )
        print()

        # Arduino standoffs (connected to base)
        standoff_positions = [
            (ARDUINO_HOLE_SPACING_L/2, ARDUINO_HOLE_SPACING_W/2),
            (-ARDUINO_HOLE_SPACING_L/2, ARDUINO_HOLE_SPACING_W/2),
            (-ARDUINO_HOLE_SPACING_L/2, -ARDUINO_HOLE_SPACING_W/2),
            (ARDUINO_HOLE_SPACING_L/2, -ARDUINO_HOLE_SPACING_W/2),
        ]

        print("Arduino Standoff Positions:")
        for i, (px, py) in enumerate(standoff_positions):
            print(f"  Standoff {i+1}: ({px:.1f}, {py:.1f}) mm, height = {STANDOFF_HEIGHT} mm")

        for px, py in standoff_positions:
            # Standoff cylinder
            with BuildSketch(Plane.XY.offset(BODY_THICKNESS)) as standoff:
                with Locations([(px, py)]):
                    Circle(STANDOFF_OD / 2)
            extrude(amount=STANDOFF_HEIGHT)

            # Screw hole through standoff and base
            Hole(STANDOFF_ID/2, depth=STANDOFF_HEIGHT + BODY_THICKNESS).locate(
                Location((px, py, BODY_THICKNESS + STANDOFF_HEIGHT))
            )
        print()

        # IMU mounting platform at center (raised)
        print(f"IMU Platform: center (0, 0), size {IMU_PLATFORM_L} x {IMU_PLATFORM_W} mm, raised {IMU_PLATFORM_HEIGHT} mm")
        with BuildSketch(Plane.XY.offset(BODY_THICKNESS)) as imu_base:
            RectangleRounded(IMU_PLATFORM_L, IMU_PLATFORM_W, radius=2)
        extrude(amount=IMU_PLATFORM_HEIGHT)

        # IMU mounting holes (M2.5)
        imu_hole_positions = [
            (IMU_HOLE_SPACING/2, IMU_HOLE_SPACING/2),
            (-IMU_HOLE_SPACING/2, IMU_HOLE_SPACING/2),
            (-IMU_HOLE_SPACING/2, -IMU_HOLE_SPACING/2),
            (IMU_HOLE_SPACING/2, -IMU_HOLE_SPACING/2),
        ]
        for ix, iy in imu_hole_positions:
            Hole(IMU_HOLE_DIA/2, depth=BODY_THICKNESS + IMU_PLATFORM_HEIGHT).locate(
                Location((ix, iy, BODY_THICKNESS + IMU_PLATFORM_HEIGHT))
            )

        # Battery rails on bottom (extending downward)
        # Rails are positioned OUTSIDE the battery compartment to hold the battery
        rail_y_offset = BATTERY_COMP_WIDTH / 2 + BATTERY_RAIL_WIDTH
        print(f"Battery Rails: Y = +/-{rail_y_offset:.1f} mm, extending to Z = -{BATTERY_RAIL_HEIGHT} mm")
        for side in [1, -1]:
            with BuildSketch(Plane.XY) as rail:
                with Locations([(0, side * rail_y_offset)]):
                    RectangleRounded(BATTERY_COMP_LENGTH + 5, BATTERY_RAIL_WIDTH, radius=1)
            extrude(amount=-BATTERY_RAIL_HEIGHT)
        print()

        # Triangular truss pattern for weight reduction (stronger than honeycomb)
        tri_positions, tri_radius = create_triangular_pattern(
            BODY_LENGTH - 35, BODY_WIDTH - 35,
            tri_size=TRUSS_HOLE_SIZE,
            wall=TRUSS_WALL
        )

        # Filter out positions that would interfere with features
        filtered_positions = []
        for tx, ty, pointing_up in tri_positions:
            too_close = False

            # Skip if too close to standoffs
            for px, py in standoff_positions:
                if math.sqrt((tx - px)**2 + (ty - py)**2) < 14:
                    too_close = True
                    break

            # Skip if too close to center (IMU)
            if math.sqrt(tx**2 + ty**2) < 20:
                too_close = True

            # Skip if in arm mount areas
            for angle in arm_angles:
                angle_rad = math.radians(angle)
                ax = ARM_MOUNT_DISTANCE * math.cos(angle_rad)
                ay = ARM_MOUNT_DISTANCE * math.sin(angle_rad)
                if math.sqrt((tx - ax)**2 + (ty - ay)**2) < 18:
                    too_close = True
                    break

            if not too_close:
                filtered_positions.append((tx, ty, pointing_up))

        # Cut triangular holes
        print(f"Truss Pattern: {len(filtered_positions)} triangular cutouts")
        print(f"  Triangle size: {TRUSS_HOLE_SIZE} mm, wall: {TRUSS_WALL} mm")
        if filtered_positions:
            with BuildSketch(Plane.XY.offset(BODY_THICKNESS)) as truss:
                for tx, ty, pointing_up in filtered_positions:
                    with Locations([(tx, ty)]):
                        # Rotate triangle based on direction
                        rot = 0 if pointing_up else 180
                        RegularPolygon(radius=tri_radius, side_count=3, rotation=rot)
            extrude(amount=-BODY_THICKNESS, mode=Mode.SUBTRACT)

        # Battery strap slots (for securing battery with strap)
        strap_positions = [20, -20]
        for sy in strap_positions:
            with BuildSketch(Plane.XY.offset(BODY_THICKNESS)) as strap:
                with Locations([(0, sy)]):
                    RectangleRounded(BATTERY_COMP_WIDTH + 10, 3, radius=1)
            extrude(amount=-BODY_THICKNESS, mode=Mode.SUBTRACT)

        print("=" * 60)

    return body.part


# Create the body
body = create_body()

if __name__ == "__main__":
    show(body)
