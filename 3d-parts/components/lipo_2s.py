"""
2S LiPo Battery - Simplified 3D model for assembly visualization.

Typical 2S 300-500mAh battery dimensions:
- Size: 50 x 25 x 12 mm (varies by capacity)
- JST-XH balance connector
- XT30 or JST power connector
"""

from build123d import *
from ocp_vscode import show

# Battery dimensions (typical 2S 300-500mAh)
BATTERY_LENGTH = 50     # mm
BATTERY_WIDTH = 25      # mm
BATTERY_HEIGHT = 12     # mm

# Connectors
POWER_CONNECTOR_SIZE = (8, 10, 6)   # XT30 or similar
BALANCE_CONNECTOR_SIZE = (8, 3, 5)  # JST-XH 3-pin


def create_lipo_2s():
    """Create a simplified 2S LiPo battery model."""

    with BuildPart() as battery:
        # Main battery body (rounded edges for realism)
        with BuildSketch() as body:
            RectangleRounded(BATTERY_LENGTH, BATTERY_WIDTH, radius=2)
        extrude(amount=BATTERY_HEIGHT)

        # Round the top edges
        edges_to_fillet = battery.edges().filter_by(Axis.Z).filter_by(
            lambda e: e.center().Z > BATTERY_HEIGHT - 1
        )
        if edges_to_fillet:
            try:
                fillet(edges_to_fillet, radius=1.5)
            except:
                pass  # Skip if fillet fails

        # Power connector (XT30) on one end
        with BuildSketch(Plane.XZ.offset(-BATTERY_WIDTH/2)) as power:
            with Locations([(BATTERY_LENGTH/2 - POWER_CONNECTOR_SIZE[0]/2 - 2, BATTERY_HEIGHT/2)]):
                Rectangle(POWER_CONNECTOR_SIZE[0], POWER_CONNECTOR_SIZE[2])
        extrude(amount=-POWER_CONNECTOR_SIZE[1])

        # Balance connector (JST-XH) next to power
        with BuildSketch(Plane.XZ.offset(-BATTERY_WIDTH/2)) as balance:
            with Locations([(BATTERY_LENGTH/2 - POWER_CONNECTOR_SIZE[0] - BALANCE_CONNECTOR_SIZE[0]/2 - 4,
                            BATTERY_HEIGHT/2)]):
                Rectangle(BALANCE_CONNECTOR_SIZE[0], BALANCE_CONNECTOR_SIZE[2])
        extrude(amount=-BALANCE_CONNECTOR_SIZE[1])

    return battery.part


lipo = create_lipo_2s()

if __name__ == "__main__":
    show(lipo)
