"""
Drone Frame Arm - Motor mount arm for 820 brushed motors.

Specifications:
- Total length: 65mm from mount plate center to motor center
- Arm cross-section: 10 x 8 mm
- Motor: 820 brushed (8mm diameter x 20mm length)
- Motor socket: 8.2mm ID (0.2mm clearance), 15mm deep
- Motor mount OD: 12mm, depth: 18mm
- Mount plate: 14 x 18 mm with M3 holes (10mm spacing)
- Prop guard attaches via friction-fit sleeve over motor mount

Geometry notes (for assembly):
- Arm is built along Y axis
- Mount plate center: Y = 0 (origin)
- Motor center: Y = +65 (ARM_TOTAL_LENGTH from mount)
"""

from build123d import *
from ocp_vscode import show

# Total arm length (mount plate center to motor center)
ARM_TOTAL_LENGTH = 65   # mm - this is the key dimension

# Arm beam dimensions
ARM_WIDTH = 10          # mm (cross-section width)
ARM_HEIGHT = 8          # mm (cross-section height)
ARM_BEAM_LENGTH = 55    # mm (main beam, shorter than total)

# Motor 820 dimensions
MOTOR_DIAMETER = 8.0    # mm
MOTOR_SOCKET_ID = 8.2   # mm (0.2mm clearance for 8mm motor)
MOTOR_MOUNT_DEPTH = 18  # mm (how tall the motor mount is)
MOTOR_SOCKET_DEPTH = 15 # mm (how deep motor sits in mount)
MOTOR_MOUNT_OD = 12     # mm outer diameter of motor mount

# Mounting to body
MOUNT_WIDTH = 14        # mm
MOUNT_LENGTH = 18       # mm
MOUNT_HOLE_DIA = 3.2    # mm (M3 clearance)
MOUNT_HOLE_SPACING = 10 # mm

# Calculated positions (for assembly.py to import)
# Origin is at mount plate center (Y=0)
# Motor is at Y = ARM_TOTAL_LENGTH
ARM_LENGTH = ARM_TOTAL_LENGTH  # Export for assembly compatibility


def create_arm(verbose=False):
    """Create a single drone arm with motor mount.

    Geometry:
    - Origin (0,0) is at mount plate center
    - Motor center is at (0, ARM_TOTAL_LENGTH) = (0, 65)
    - Arm beam runs from mount plate to just before motor
    - Prop guard friction-fits over the motor mount cylinder
    """

    # Key positions along Y axis (mount plate at origin)
    mount_plate_y = 0
    arm_beam_start_y = MOUNT_LENGTH / 2  # Where arm beam starts (9mm from origin)
    motor_center_y = ARM_TOTAL_LENGTH    # 65mm from origin

    if verbose:
        print("=" * 50)
        print("FRAME ARM GEOMETRY")
        print("=" * 50)
        print(f"Mount plate center: Y = {mount_plate_y} mm (origin)")
        print(f"Arm beam starts: Y = {arm_beam_start_y} mm")
        print(f"Motor center: Y = {motor_center_y} mm")
        print(f"Total length (mount to motor): {ARM_TOTAL_LENGTH} mm")
        print(f"Motor mount OD: {MOTOR_MOUNT_OD} mm (for guard friction fit)")
        print("=" * 50)

    with BuildPart() as arm:
        # Mount plate at origin
        with BuildSketch(Plane.XY) as mount_plate:
            with Locations([(0, mount_plate_y)]):
                RectangleRounded(MOUNT_WIDTH, MOUNT_LENGTH, radius=2)
        extrude(amount=ARM_HEIGHT)

        # Main arm beam - from mount plate edge toward motor
        beam_length = motor_center_y - arm_beam_start_y - MOTOR_MOUNT_OD/2
        beam_center_y = arm_beam_start_y + beam_length/2
        with BuildSketch(Plane.XY) as arm_beam:
            with Locations([(0, beam_center_y)]):
                Rectangle(ARM_WIDTH, beam_length)
        extrude(amount=ARM_HEIGHT)

        # Motor mount cylinder at motor position
        with BuildSketch(Plane.XY) as motor_base:
            with Locations([(0, motor_center_y)]):
                Circle(MOTOR_MOUNT_OD / 2)
        extrude(amount=ARM_HEIGHT + MOTOR_MOUNT_DEPTH)

        # Motor socket hole (8.2mm ID for 8mm motor with clearance)
        Hole(MOTOR_SOCKET_ID/2, depth=MOTOR_SOCKET_DEPTH + 2).locate(
            Location((0, motor_center_y, ARM_HEIGHT + MOTOR_MOUNT_DEPTH))
        )

        # Mounting holes on mount plate
        for dx in [-MOUNT_HOLE_SPACING/2, MOUNT_HOLE_SPACING/2]:
            Hole(MOUNT_HOLE_DIA/2, depth=ARM_HEIGHT).locate(
                Location((dx, mount_plate_y, ARM_HEIGHT))
            )

        # Weight reduction slots in arm beam
        slot_spacing = beam_length / 4
        for i in range(3):
            slot_y = arm_beam_start_y + slot_spacing * (i + 1)
            if slot_y < motor_center_y - MOTOR_MOUNT_OD:
                with BuildSketch(Plane.XY.offset(ARM_HEIGHT)) as slot:
                    with Locations([(0, slot_y)]):
                        RectangleRounded(ARM_WIDTH - 4, 8, radius=2)
                extrude(amount=-ARM_HEIGHT + 2, mode=Mode.SUBTRACT)

        # Wire channel through arm (for motor wires)
        wire_length = motor_center_y - arm_beam_start_y + 5
        Hole(1.5, depth=wire_length).locate(
            Location((0, motor_center_y, ARM_HEIGHT/2), (90, 0, 0))
        )

    return arm.part


# Create the arm
arm = create_arm()

if __name__ == "__main__":
    show(arm)
