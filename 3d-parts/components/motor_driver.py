"""
Motor Driver Module - DRV8833 dual H-bridge for 820 brushed motors.

The DRV8833 is a compact, efficient MOSFET-based driver with minimal voltage drop.
Ideal for small brushed motors running from low voltage sources.

Specifications:
- PCB size: 18 x 12 mm
- Height: ~3mm
- Current: 1.5A per channel (peak 2A)
- Voltage: 2.7V - 10.8V
- Minimal voltage drop (~0.2V vs L298N's 2V drop)
- Weight: ~1g
"""

from build123d import *
from ocp_vscode import show

# DRV8833 module dimensions
PCB_LENGTH = 18         # mm
PCB_WIDTH = 12          # mm
PCB_THICKNESS = 1.0     # mm

# Component height
COMPONENT_HEIGHT = 2    # mm (IC + capacitors)

# Mounting holes (some modules have them, some don't)
HOLE_SPACING_L = 14     # mm
HOLE_SPACING_W = 8      # mm
HOLE_DIA = 2.0          # mm (M2 or smaller)


def create_motor_driver():
    """Create a simplified DRV8833 motor driver module model."""

    with BuildPart() as driver:
        # Main PCB
        with BuildSketch() as pcb:
            RectangleRounded(PCB_LENGTH, PCB_WIDTH, radius=0.5)
        extrude(amount=PCB_THICKNESS)

        # Mounting holes (if present on module)
        hole_positions = [
            (HOLE_SPACING_L/2, HOLE_SPACING_W/2),
            (-HOLE_SPACING_L/2, -HOLE_SPACING_W/2),
        ]
        for hx, hy in hole_positions:
            Hole(HOLE_DIA/2, depth=PCB_THICKNESS).locate(
                Location((hx, hy, PCB_THICKNESS))
            )

        # DRV8833 IC (center, small QFN package)
        with BuildSketch(Plane.XY.offset(PCB_THICKNESS)) as ic:
            with Locations([(0, 0)]):
                Rectangle(4, 4)
        extrude(amount=1)

        # Decoupling capacitors (2x small)
        cap_positions = [(6, 0), (-6, 0)]
        for cx, cy in cap_positions:
            with BuildSketch(Plane.XY.offset(PCB_THICKNESS)) as cap:
                with Locations([(cx, cy)]):
                    Rectangle(2, 1)
            extrude(amount=0.8)

        # Pin headers (6-pin on each side)
        for side in [-1, 1]:
            with BuildSketch(Plane.XY.offset(PCB_THICKNESS)) as header:
                with Locations([(0, side * (PCB_WIDTH/2 - 1.5))]):
                    Rectangle(PCB_LENGTH - 4, 2)
            extrude(amount=COMPONENT_HEIGHT)

    return driver.part


motor_driver = create_motor_driver()

if __name__ == "__main__":
    show(motor_driver)
