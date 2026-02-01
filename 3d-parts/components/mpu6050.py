"""
MPU6050 / GY-521 IMU Module - Simplified 3D model for assembly visualization.

Dimensions:
- PCB size: 21 x 16 mm
- Mounting holes: 4x M2.5, spacing 15.24mm (0.6") square
- Total height: ~4mm
"""

from build123d import *
from ocp_vscode import show

# GY-521 module dimensions
PCB_LENGTH = 21         # mm
PCB_WIDTH = 16          # mm
PCB_THICKNESS = 1.2     # mm

# Mounting holes (0.6 inch = 15.24mm square pattern)
HOLE_SPACING = 15.24    # mm
HOLE_DIA = 2.6          # mm (M2.5 clearance)

# MPU6050 chip
CHIP_SIZE = (4, 4, 1)   # QFN package

# Pin header
HEADER_PINS = 8
HEADER_PITCH = 2.54     # mm


def create_mpu6050():
    """Create a simplified MPU6050/GY-521 module model."""

    with BuildPart() as imu:
        # Main PCB (blue/purple typical)
        with BuildSketch() as pcb:
            RectangleRounded(PCB_LENGTH, PCB_WIDTH, radius=1)
        extrude(amount=PCB_THICKNESS)

        # Mounting holes
        hole_positions = [
            (HOLE_SPACING/2, HOLE_SPACING/2),
            (-HOLE_SPACING/2, HOLE_SPACING/2),
            (-HOLE_SPACING/2, -HOLE_SPACING/2),
            (HOLE_SPACING/2, -HOLE_SPACING/2),
        ]
        for hx, hy in hole_positions:
            Hole(HOLE_DIA/2, depth=PCB_THICKNESS).locate(
                Location((hx, hy, PCB_THICKNESS))
            )

        # MPU6050 chip (center of board)
        with BuildSketch(Plane.XY.offset(PCB_THICKNESS)) as chip:
            with Locations([(0, 1)]):
                Rectangle(CHIP_SIZE[0], CHIP_SIZE[1])
        extrude(amount=CHIP_SIZE[2])

        # Voltage regulator (small SOT-23)
        with BuildSketch(Plane.XY.offset(PCB_THICKNESS)) as vreg:
            with Locations([(-6, 1)]):
                Rectangle(3, 1.5)
        extrude(amount=1)

        # Pin header (8 pins on one edge)
        header_length = HEADER_PINS * HEADER_PITCH
        with BuildSketch(Plane.XY.offset(PCB_THICKNESS)) as header:
            with Locations([(0, -PCB_WIDTH/2 + 2)]):
                Rectangle(header_length, 2.5)
        extrude(amount=2.5)

    return imu.part


mpu6050 = create_mpu6050()

if __name__ == "__main__":
    show(mpu6050)
