"""
Arduino R4 WiFi - Simplified 3D model for assembly visualization.

Dimensions from official datasheet:
- PCB size: 68.5 x 53.4 mm
- Mounting holes: 4x M3, spacing 66 x 48 mm
- Total height with components: ~15mm
- USB-C connector on short edge
"""

from build123d import *
from ocp_vscode import show, set_defaults

# Arduino R4 WiFi dimensions
PCB_LENGTH = 68.5       # mm
PCB_WIDTH = 53.4        # mm
PCB_THICKNESS = 1.6     # mm
COMPONENT_HEIGHT = 12   # mm (tallest component)

# Mounting holes
HOLE_SPACING_L = 66.0   # mm
HOLE_SPACING_W = 48.0   # mm
HOLE_DIA = 3.2          # mm (M3 clearance)

# USB-C connector
USB_WIDTH = 9           # mm
USB_HEIGHT = 3.5        # mm
USB_DEPTH = 7           # mm

# Major components (simplified blocks)
MICROCONTROLLER_SIZE = (12, 12, 2)  # Renesas RA4M1
WIFI_MODULE_SIZE = (18, 12, 3)      # ESP32-S3
BARREL_JACK_SIZE = (9, 14, 11)      # DC power jack


def create_arduino_r4():
    """Create a simplified Arduino R4 WiFi model."""

    with BuildPart() as arduino:
        # Main PCB (green)
        with BuildSketch() as pcb:
            RectangleRounded(PCB_LENGTH, PCB_WIDTH, radius=2)
        extrude(amount=PCB_THICKNESS)

        # Mounting holes
        hole_positions = [
            (HOLE_SPACING_L/2, HOLE_SPACING_W/2),
            (-HOLE_SPACING_L/2, HOLE_SPACING_W/2),
            (-HOLE_SPACING_L/2, -HOLE_SPACING_W/2),
            (HOLE_SPACING_L/2, -HOLE_SPACING_W/2),
        ]
        for hx, hy in hole_positions:
            Hole(HOLE_DIA/2, depth=PCB_THICKNESS).locate(
                Location((hx, hy, PCB_THICKNESS))
            )

        # USB-C connector (on +X edge)
        with BuildSketch(Plane.XY.offset(PCB_THICKNESS)) as usb:
            with Locations([(PCB_LENGTH/2 - USB_DEPTH/2, 0)]):
                Rectangle(USB_DEPTH, USB_WIDTH)
        extrude(amount=USB_HEIGHT)

        # Barrel jack (on +X edge, offset)
        with BuildSketch(Plane.XY.offset(PCB_THICKNESS)) as barrel:
            with Locations([(PCB_LENGTH/2 - BARREL_JACK_SIZE[1]/2, -PCB_WIDTH/2 + BARREL_JACK_SIZE[0]/2 + 5)]):
                Rectangle(BARREL_JACK_SIZE[1], BARREL_JACK_SIZE[0])
        extrude(amount=BARREL_JACK_SIZE[2])

        # Microcontroller chip (center-ish)
        with BuildSketch(Plane.XY.offset(PCB_THICKNESS)) as mcu:
            with Locations([(5, 8)]):
                Rectangle(MICROCONTROLLER_SIZE[0], MICROCONTROLLER_SIZE[1])
        extrude(amount=MICROCONTROLLER_SIZE[2])

        # WiFi module (ESP32-S3)
        with BuildSketch(Plane.XY.offset(PCB_THICKNESS)) as wifi:
            with Locations([(-15, -10)]):
                Rectangle(WIFI_MODULE_SIZE[0], WIFI_MODULE_SIZE[1])
        extrude(amount=WIFI_MODULE_SIZE[2])

        # Pin headers (simplified as blocks)
        # Long headers on sides
        header_height = 8.5
        for side in [1, -1]:
            with BuildSketch(Plane.XY.offset(PCB_THICKNESS)) as header:
                with Locations([(0, side * (PCB_WIDTH/2 - 3))]):
                    Rectangle(PCB_LENGTH - 20, 2.5)
            extrude(amount=header_height)

    return arduino.part


arduino = create_arduino_r4()

if __name__ == "__main__":
    set_defaults(axes=True, axes0=True, grid=[True, False, False])
    show(arduino)
