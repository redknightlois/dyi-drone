"""
LM2596 DC-DC Buck Converter Module - Enclosure.

Creates:
1. create_enclosure() - 3D-printable hollow enclosure with cutouts and vents
2. create_lid()       - Friction-fit lid with display window and reset button hole
3. create_assembly()  - Enclosure + lid positioned for visualization

Enclosure features:
- Hollow box with open top (75 x 48 x 15 mm, 2mm walls)
- 4 corner standoffs for PCB clearance (3mm height)
- Terminal cutouts on both short ends (±X walls)
- 4-slot ventilation pattern on ±Y long walls
"""

from build123d import *
from ocp_vscode import show, set_defaults

# =============================================================================
# PCB REFERENCE DIMENSIONS (LM2596 module)
# =============================================================================
DISPLAY_LENGTH = 22     # mm
DISPLAY_WIDTH = 13      # mm

POT_LID_DIA = 5.0       # mm - lid hole for screwdriver access
RESET_BTN_SIZE = 5.0    # mm - reset button hole (square)
LED_DIA = 2.5           # mm - hole diameter for LED visibility
CABLE_HOLE_DIA = 3.0    # mm - hole for wires to pass through lid
CABLE_HOLE_SPACING = 5.0  # mm - center-to-center distance between cable holes

PCB_HOLE_DIA = 3.0          # mm (M3)

# =============================================================================
# ENCLOSURE DIMENSIONS
# =============================================================================
WALL = 2.0              # mm - wall and floor thickness

# Corner bosses (4 corners, square pillars anchored to interior walls)
STANDOFF_DIA = 5.0      # mm (square side length)
BOSS_CLEARANCE = 3.0    # mm - gap between boss and inner wall for PCB insertion

BOX_L = 74.0            # mm (X) - fits 52mm inner boss spacing
BOX_W = 48.0            # mm (Y) - fits 27mm inner boss spacing
BOX_H = 15.0            # mm (Z) - outer height
STANDOFF_HEIGHT = 3.0   # mm above interior floor

# Terminal cutouts (on ±X end walls)
TERM_CUT_WIDTH = 12.0   # mm (Y direction)
TERM_CUT_HEIGHT = 10.0  # mm (Z direction)

# Ventilation slots (4 per wall face)
VENT_WIDTH = 2.0        # mm per slot
VENT_HEIGHT = 12.0      # mm per slot
VENT_GAP = 2.0          # mm between slots
VENT_COUNT = 4          # slots per wall face



def create_enclosure():
    """Create a 3D-printable hollow enclosure for the LM2596 module.

    Open-top box (75 × 48 × 15 mm, 2mm walls) with:
    - Terminal cutouts on ±X short walls
    - 4-slot ventilation on ±Y long walls
    - Corner standoffs with M3 holes
    Coordinate system (origin at center-bottom of box):
        X: ±BOX_L/2 = ±37.5   (short end walls at ±X)
        Y: ±BOX_W/2 = ±24     (long side walls at ±Y)
        Z: 0 = base,  BOX_H = top rim
    """

    # Vent slot X-offsets (centered pattern for 4 slots)
    slot_pitch = VENT_WIDTH + VENT_GAP
    slot_offsets = [
        (i - (VENT_COUNT - 1) / 2) * slot_pitch
        for i in range(VENT_COUNT)
    ]

    with BuildPart() as enclosure:
        # =================================================================
        # Step 1: Outer shell — base at Z=0
        # =================================================================
        Box(BOX_L, BOX_W, BOX_H,
            align=(Align.CENTER, Align.CENTER, Align.MIN))

        # =================================================================
        # Step 2: Hollow interior (open top)
        # =================================================================
        with Locations([(0, 0, WALL)]):
            Box(BOX_L - 2 * WALL, BOX_W - 2 * WALL, BOX_H,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT)

        # =================================================================
        # Step 3: Square corner bosses with centered M3 holes
        # =================================================================
        boss_cx = BOX_L / 2 - WALL - BOSS_CLEARANCE - STANDOFF_DIA / 2
        boss_cy = BOX_W / 2 - WALL - BOSS_CLEARANCE - STANDOFF_DIA / 2
        boss_positions = [
            ( boss_cx,  boss_cy),
            (-boss_cx,  boss_cy),
            (-boss_cx, -boss_cy),
            ( boss_cx, -boss_cy),
        ]
        with BuildSketch(Plane.XY.offset(WALL)):
            for bx, by in boss_positions:
                with Locations([(bx, by)]):
                    Rectangle(STANDOFF_DIA, STANDOFF_DIA)
                    Circle(PCB_HOLE_DIA / 2, mode=Mode.SUBTRACT)
        extrude(amount=STANDOFF_HEIGHT)

        # =================================================================
        # Step 4: Terminal cutouts — ±X short walls
        # =================================================================
        term_z = WALL + TERM_CUT_HEIGHT / 2
        for x_sign in [1, -1]:
            with Locations([(x_sign * BOX_L / 2, 0, term_z)]):
                Box(WALL * 3, TERM_CUT_WIDTH, TERM_CUT_HEIGHT,
                    mode=Mode.SUBTRACT)

        # =================================================================
        # Step 5: Ventilation slots — ±Y long side walls
        # =================================================================
        slot_z = BOX_H / 2
        for y_sign in [1, -1]:
            for x_off in slot_offsets:
                with Locations([(x_off, y_sign * BOX_W / 2, slot_z)]):
                    Box(VENT_WIDTH, WALL * 3, VENT_HEIGHT,
                        mode=Mode.SUBTRACT)

    return enclosure.part


def create_lid():
    """Create a friction-fit lid for the LM2596 enclosure.

    Cutout positions computed relative to lid dimensions.
    Orientation: Main plate at Z=0, rim extends downward (-Z).
    Rim: 0.25mm tolerance from inner walls, 12mm gaps at ±X for wires.
    """

    LID_THICKNESS = WALL  # 2.0 mm
    RIM_TOLERANCE = 0.25  # mm clearance per side for friction fit
    RIM_HEIGHT = 3.0      # mm - depth of rim that goes into box
    TERMINAL_GAP = 12.0   # mm - gap width at ±X walls for wire clearance

    # Rim dimensions (sits inside box walls with tolerance)
    RIM_LENGTH = BOX_L - 2 * WALL - 2 * RIM_TOLERANCE
    RIM_WIDTH = BOX_W - 2 * WALL - 2 * RIM_TOLERANCE

    # --- Relative position calculations ---
    # Usable interior area (inside walls)
    inner_l = BOX_L - 2 * WALL   # 71mm
    inner_w = BOX_W - 2 * WALL   # 44mm

    # Display: centered X, upper quarter Y
    display_x = 0
    display_y = inner_w / 4                    # ~9.5mm toward +Y (top)

    # LEDs: centered X (flanking display), near top edge
    led_y = inner_w / 2 - LED_DIA - 1         # ~16mm, near +Y edge
    led_in_x = -DISPLAY_LENGTH / 4             # -5.5mm (left of center)
    led_out_x = DISPLAY_LENGTH / 4             # +5.5mm (right of center)

    # Cable holes: at +X wall
    cable_x = inner_l / 2 - CABLE_HOLE_DIA / 2 - 3  # 3mm inset from +X inner wall
    cable_y1 = CABLE_HOLE_SPACING / 2              # two holes, 5mm apart
    cable_y2 = -CABLE_HOLE_SPACING / 2

    # Pot: below display, left of center
    pot_x = -inner_l / 6 + STANDOFF_DIA - 2     # ~-8.8mm
    pot_y = -inner_w / 4 - STANDOFF_DIA        # ~-16mm

    # Reset button: +Y edge aligned with display top edge
    reset_btn_x = -(inner_l / 2 - STANDOFF_DIA * 2)
    display_top_y = display_y + DISPLAY_WIDTH / 2      # +Y edge of display
    reset_btn_y = display_top_y - RESET_BTN_SIZE / 2   # align +Y edges

    # Full depth for through-holes
    cut_depth = LID_THICKNESS + RIM_HEIGHT + 1

    with BuildPart() as lid:
        # =================================================================
        # Step 1: Main plate (top surface at Z=0)
        # =================================================================
        Box(BOX_L, BOX_W, LID_THICKNESS,
            align=(Align.CENTER, Align.CENTER, Align.MIN))

        # =================================================================
        # Step 2: Friction-fit rim with 12mm terminal gaps at ±X walls
        # =================================================================
        with BuildSketch(Plane.XY.offset(-RIM_HEIGHT)):
            # ±Y long walls (continuous)
            with Locations([(0, RIM_WIDTH / 2)]):
                Rectangle(RIM_LENGTH, WALL)
            with Locations([(0, -RIM_WIDTH / 2)]):
                Rectangle(RIM_LENGTH, WALL)
            # ±X short walls (split with 12mm center gap for terminal wires)
            x_rim_height = RIM_WIDTH - TERMINAL_GAP  # usable Y span
            with Locations([(RIM_LENGTH / 2, 0)]):
                Rectangle(WALL, x_rim_height)
            with Locations([(-RIM_LENGTH / 2, 0)]):
                Rectangle(WALL, x_rim_height)
        extrude(amount=RIM_HEIGHT)

        # =================================================================
        # Step 3: Display window — centered, upper area
        # =================================================================
        with Locations([(display_x, display_y, 0)]):
            Box(DISPLAY_LENGTH, DISPLAY_WIDTH, cut_depth,
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
                mode=Mode.SUBTRACT)

        # =================================================================
        # Step 4: LED indicator holes — above display, near top edge
        # =================================================================
        with BuildSketch(Plane.XY.offset(LID_THICKNESS)):
            for lx in [led_in_x, led_out_x]:
                with Locations([(lx, led_y)]):
                    Circle(LED_DIA / 2)
        extrude(amount=-cut_depth, mode=Mode.SUBTRACT)

        # =================================================================
        # Step 5: Cable holes — +X edge
        # =================================================================
        with BuildSketch(Plane.XY.offset(LID_THICKNESS)):
            for cy in [cable_y1, cable_y2]:
                with Locations([(cable_x, cy)]):
                    Circle(CABLE_HOLE_DIA / 2)
        extrude(amount=-cut_depth, mode=Mode.SUBTRACT)

        # =================================================================
        # Step 6: Potentiometer hole — below display, left of center
        # =================================================================
        with BuildSketch(Plane.XY.offset(LID_THICKNESS)):
            with Locations([(pot_x, pot_y)]):
                Circle(POT_LID_DIA / 2)
        extrude(amount=-cut_depth, mode=Mode.SUBTRACT)

        # =================================================================
        # Step 7: Reset button hole (square) — -X side, +Y aligned with display
        # =================================================================
        with Locations([(reset_btn_x, reset_btn_y, 0)]):
            Box(RESET_BTN_SIZE, RESET_BTN_SIZE, cut_depth,
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
                mode=Mode.SUBTRACT)

    return lid.part


def create_assembly():
    """Create assembly showing enclosure + lid positioned correctly."""
    enclosure = create_enclosure()
    lid = create_lid()

    # Lid sits at top of enclosure
    lid_z = BOX_H  # 15mm

    return (
        enclosure,
        lid.locate(Location((0, 0, lid_z))),
    )


if __name__ == "__main__":
    set_defaults(axes=True, axes0=True, grid=[True, False, False])
    enclosure = create_enclosure()
    lid = create_lid()
    # Display lid raised above enclosure for clarity
    lid_raised = lid.move(Pos(0, 0, BOX_H + 10))
    show(enclosure, lid_raised, names=["Enclosure", "Lid"])
