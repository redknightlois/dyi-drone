"""
Drone Frame Assembly - Complete drone frame visualization.

Combines all parts:
- 1x Frame body (center)
- 4x Arms (at 45 degree positions)
- 4x Prop guards (on each arm)
- 1x Battery cover (bottom)
"""

from build123d import *
from ocp_vscode import show
import math

# Import individual parts
from frame_body import create_body
from frame_arm import create_arm, ARM_TOTAL_LENGTH, ARM_HEIGHT, MOTOR_MOUNT_DEPTH
from prop_guard import create_prop_guard
from battery_cover import create_battery_cover

# Assembly constants (matching frame_body.py)
ARM_MOUNT_DISTANCE = 40  # mm from center (diagonal) - where arm attaches to body
BODY_THICKNESS = 4       # mm
ARM_PLATFORM_HEIGHT = 4  # mm - the raised platform on body for arm mounting


def rotate_point(x, y, angle_deg):
    """Rotate a 2D point around origin by angle in degrees."""
    angle_rad = math.radians(angle_deg)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    return (x * cos_a - y * sin_a, x * sin_a + y * cos_a)


def create_assembly():
    """Create the complete drone assembly."""

    print("\n" + "=" * 60)
    print("DRONE ASSEMBLY POSITIONS")
    print("=" * 60)

    # Create body first
    body = create_body()

    # Store parts separately for colored display
    body_parts = [body]
    arm_parts = []
    guard_parts = []
    cover_parts = []

    print("\nBody: center at (0, 0, 0)")

    # Z position where arms sit
    arm_z = BODY_THICKNESS + ARM_PLATFORM_HEIGHT

    # Arm geometry (new simplified design):
    # - Mount plate center at origin (Y=0)
    # - Motor center at Y = ARM_TOTAL_LENGTH (65mm)
    print(f"\nArm Geometry (simplified):")
    print(f"  Mount plate at origin (Y=0)")
    print(f"  Motor at Y = {ARM_TOTAL_LENGTH} mm")
    print(f"  Arms placed at Z = {arm_z} mm")

    # Add 4 arms at 45 degree positions
    arm_configs = [
        (45, "Front-Right"),
        (135, "Front-Left"),
        (225, "Rear-Left"),
        (315, "Rear-Right"),
    ]

    print(f"\nArm Positions:")
    for angle, name in arm_configs:
        # Body mount position
        angle_rad = math.radians(angle)
        body_mount_x = ARM_MOUNT_DISTANCE * math.cos(angle_rad)
        body_mount_y = ARM_MOUNT_DISTANCE * math.sin(angle_rad)

        # Arm rotation: +Y should point outward at 'angle'
        # +Y is at 90° in standard coords, so rotate by (angle - 90)
        arm_rotation = angle - 90

        # Since mount plate is at arm origin, arm origin = body mount position
        arm_x = body_mount_x
        arm_y = body_mount_y

        # Motor position: (0, ARM_TOTAL_LENGTH) rotated by arm_rotation, then translated
        motor_local = rotate_point(0, ARM_TOTAL_LENGTH, arm_rotation)
        motor_x = arm_x + motor_local[0]
        motor_y = arm_y + motor_local[1]
        motor_distance = math.sqrt(motor_x**2 + motor_y**2)

        print(f"  {name} ({angle}°):")
        print(f"    Arm mount/origin: ({arm_x:.1f}, {arm_y:.1f})")
        print(f"    Motor position: ({motor_x:.1f}, {motor_y:.1f})")
        print(f"    Motor distance from center: {motor_distance:.1f} mm")

        # Create and position arm
        arm_part = create_arm()
        arm_located = Pos(arm_x, arm_y, arm_z) * Rot(0, 0, arm_rotation) * arm_part
        arm_parts.append(arm_located)

        # Position prop guard at motor location
        # Guard clip is at -X in guard coords
        # Rotate guard so clip points toward body center (at angle + 180 from motor)
        guard_rotation = angle

        guard_part = create_prop_guard()
        guard_located = Pos(motor_x, motor_y, arm_z) * Rot(0, 0, guard_rotation) * guard_part
        guard_parts.append(guard_located)

    # Add battery cover at bottom
    print(f"\nBattery Cover: at (0, 0, -8), flipped")

    cover_part = create_battery_cover()
    cover_located = Pos(0, 0, -8) * Rot(180, 0, 0) * cover_part
    cover_parts.append(cover_located)

    print("\n" + "=" * 60)

    return body_parts, arm_parts, guard_parts, cover_parts


# Create the assembly
body_parts, arm_parts, guard_parts, cover_parts = create_assembly()

if __name__ == "__main__":
    # Display with different colors for each part type
    show(
        *body_parts,
        *arm_parts,
        *guard_parts,
        *cover_parts,
        names=["Body"] + [f"Arm {i+1}" for i in range(4)] + [f"Guard {i+1}" for i in range(4)] + ["Battery Cover"],
        colors=[
            "#505050",       # Body - dark gray
            "#4682B4",       # Arms - steel blue
            "#4682B4",
            "#4682B4",
            "#4682B4",
            "#FF6600",       # Guards - orange (high visibility)
            "#FF6600",
            "#FF6600",
            "#FF6600",
            "#228B22",       # Battery cover - forest green
        ]
    )
