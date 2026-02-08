"""
Drone Frame Assembly - Complete drone frame visualization with electronics.

Combines all parts:
- 1x Frame body (center)
- 4x Arms (at 45 degree positions)
- 4x Prop guards (on each arm)
- 1x Battery cover (bottom)

Electronics:
- 1x Arduino R4 WiFi (on standoffs)
- 1x MPU6050 IMU (center platform)
- 1x 2S LiPo Battery (bottom compartment)
- 1x Motor Driver (mounted on body)
"""

from build123d import *
from ocp_vscode import show, set_defaults
import math

# Import frame parts
from frame_body import create_body
from frame_arm import create_arm, ARM_TOTAL_LENGTH, ARM_HEIGHT, MOTOR_MOUNT_DEPTH
from prop_guard import create_prop_guard
from battery_cover import create_battery_cover

# Import electronic components
from components import create_arduino_r4, create_mpu6050, create_lipo_2s, create_motor_driver

# Assembly constants (matching frame_body.py)
ARM_MOUNT_DISTANCE = 40  # mm from center (diagonal)
BODY_THICKNESS = 4       # mm
ARM_PLATFORM_HEIGHT = 4  # mm

# Component mounting heights
ARDUINO_STANDOFF_HEIGHT = 8   # mm
IMU_PLATFORM_HEIGHT = 2       # mm


def rotate_point(x, y, angle_deg):
    """Rotate a 2D point around origin by angle in degrees."""
    angle_rad = math.radians(angle_deg)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    return (x * cos_a - y * sin_a, x * sin_a + y * cos_a)


def create_assembly(include_electronics=True):
    """Create the complete drone assembly.

    Args:
        include_electronics: If True, include Arduino, IMU, battery, and driver
    """

    print("\n" + "=" * 60)
    print("DRONE ASSEMBLY")
    print("=" * 60)

    # Create body first
    body = create_body()

    # Store parts by category for colored display
    body_parts = [body]
    arm_parts = []
    guard_parts = []
    cover_parts = []
    electronics_parts = []

    print("\nFrame Components:")
    print("  Body: center at (0, 0, 0)")

    # Z position where arms sit
    arm_z = BODY_THICKNESS + ARM_PLATFORM_HEIGHT

    # Add 4 arms at 45 degree positions
    arm_configs = [
        (45, "Front-Right"),
        (135, "Front-Left"),
        (225, "Rear-Left"),
        (315, "Rear-Right"),
    ]

    for angle, name in arm_configs:
        angle_rad = math.radians(angle)
        body_mount_x = ARM_MOUNT_DISTANCE * math.cos(angle_rad)
        body_mount_y = ARM_MOUNT_DISTANCE * math.sin(angle_rad)
        arm_rotation = angle - 90

        # Motor position: arm extends from mount toward 'angle' direction
        # Motor is ARM_TOTAL_LENGTH away from mount, along the arm direction (which is 'angle')
        motor_x = body_mount_x + ARM_TOTAL_LENGTH * math.cos(angle_rad)
        motor_y = body_mount_y + ARM_TOTAL_LENGTH * math.sin(angle_rad)
        motor_distance = math.sqrt(motor_x**2 + motor_y**2)

        print(f"  Arm {name}: mount ({body_mount_x:.1f}, {body_mount_y:.1f}), motor ({motor_x:.1f}, {motor_y:.1f}), dist={motor_distance:.1f}mm")

        # Create and position arm
        arm_part = create_arm()
        arm_located = Pos(body_mount_x, body_mount_y, arm_z) * Rot(0, 0, arm_rotation) * arm_part
        arm_parts.append(arm_located)

        # Position prop guard at motor location
        # Guard has a central sleeve that slides over the motor mount
        # Sleeve extends 10mm down from guard base (Z=0 in guard coords)
        # Position guard so sleeve bottom aligns with arm top
        # Motor mount top is at: arm_z + ARM_HEIGHT + MOTOR_MOUNT_DEPTH
        # We want guard sleeve to cover upper part of motor mount
        motor_mount_top_z = arm_z + ARM_HEIGHT + MOTOR_MOUNT_DEPTH
        guard_z = motor_mount_top_z - 8  # Sleeve covers top 8mm of motor mount

        guard_rotation = angle
        guard_part = create_prop_guard()
        guard_located = Pos(motor_x, motor_y, guard_z) * Rot(0, 0, guard_rotation) * guard_part
        guard_parts.append(guard_located)

    # Add battery cover at bottom
    cover_part = create_battery_cover()
    cover_located = Pos(0, 0, -8) * Rot(180, 0, 0) * cover_part
    cover_parts.append(cover_located)
    print("  Battery Cover: (0, 0, -8)")

    # Add electronics if requested
    if include_electronics:
        print("\nElectronic Components:")

        # Arduino R4 WiFi - on standoffs above body
        arduino_z = BODY_THICKNESS + ARDUINO_STANDOFF_HEIGHT
        arduino = create_arduino_r4()
        arduino_located = Pos(0, 0, arduino_z) * arduino
        electronics_parts.append(("arduino", arduino_located))
        print(f"  Arduino R4 WiFi: (0, 0, {arduino_z})")

        # MPU6050 IMU - on center platform
        imu_z = BODY_THICKNESS + IMU_PLATFORM_HEIGHT
        imu = create_mpu6050()
        imu_located = Pos(0, 0, imu_z) * imu
        electronics_parts.append(("imu", imu_located))
        print(f"  MPU6050 IMU: (0, 0, {imu_z})")

        # 2S LiPo Battery - in bottom compartment
        battery_z = -3  # Sits in the rail area
        battery = create_lipo_2s()
        # Rotate to fit in the battery bay
        battery_located = Pos(0, 0, battery_z) * Rot(180, 0, 0) * battery
        electronics_parts.append(("battery", battery_located))
        print(f"  2S LiPo Battery: (0, 0, {battery_z})")

        # DRV8833 Motor Drivers - need 2 boards for 4 motors (2 channels each)
        # Each board is 18x12mm, fits easily on the body
        driver_z = BODY_THICKNESS + 1  # Slightly raised

        # Driver 1: Front-Right and Front-Left motors
        driver1 = create_motor_driver()
        driver1_located = Pos(20, 10, driver_z) * driver1
        electronics_parts.append(("driver1", driver1_located))
        print(f"  DRV8833 #1: (20, 10, {driver_z}) - Front motors")

        # Driver 2: Rear-Left and Rear-Right motors
        driver2 = create_motor_driver()
        driver2_located = Pos(20, -10, driver_z) * driver2
        electronics_parts.append(("driver2", driver2_located))
        print(f"  DRV8833 #2: (20, -10, {driver_z}) - Rear motors")

    print("\n" + "=" * 60)

    return body_parts, arm_parts, guard_parts, cover_parts, electronics_parts


# Create the assembly
body_parts, arm_parts, guard_parts, cover_parts, electronics_parts = create_assembly(include_electronics=True)

if __name__ == "__main__":
    set_defaults(axes=True, axes0=True, grid=[True, False, False])
    # Collect all parts for display
    all_parts = []
    all_names = []
    all_colors = []

    # Frame parts
    all_parts.extend(body_parts)
    all_names.append("Body")
    all_colors.append("#505050")  # Dark gray

    for i, arm in enumerate(arm_parts):
        all_parts.append(arm)
        all_names.append(f"Arm {i+1}")
        all_colors.append("#4682B4")  # Steel blue

    for i, guard in enumerate(guard_parts):
        all_parts.append(guard)
        all_names.append(f"Guard {i+1}")
        all_colors.append("#FF6600")  # Orange

    all_parts.extend(cover_parts)
    all_names.append("Battery Cover")
    all_colors.append("#228B22")  # Forest green

    # Electronics with distinct colors
    electronics_colors = {
        "arduino": "#006400",   # Dark green (PCB)
        "imu": "#4B0082",       # Indigo (purple PCB)
        "battery": "#1E90FF",   # Dodger blue (battery wrap)
        "driver1": "#8B0000",   # Dark red (PCB)
        "driver2": "#8B0000",   # Dark red (PCB)
    }

    for name, part in electronics_parts:
        all_parts.append(part)
        all_names.append(name.replace("_", " ").title())
        all_colors.append(electronics_colors.get(name, "#808080"))

    # Display with colors
    show(
        *all_parts,
        names=all_names,
        colors=all_colors,
    )
