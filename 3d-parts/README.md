# Drone Frame 3D Parts

3D printable frame for a micro drone with 2.5" propellers.

## Specifications

| Parameter | Value |
|-----------|-------|
| Propellers | 2.5" (63.5mm diameter) |
| Motors | 820 Coreless Brushed (8mm x 20mm) |
| Motor Voltage | DC 3.7V (via voltage regulator from 7.4V) |
| Motor RPM | 43,000-50,000 RPM |
| Controller | Arduino R4 WiFi |
| IMU | MPU6050 |
| Motor Driver | 2× DRV8833 (18×12mm each, 1.5A/channel) |
| Battery | LiPo 2S (7.4V, 300-500mAh) |
| Target Weight | ~100g total |
| Print Bed | 220x220mm (Ender 3 V3 SE) |

> **Note:** The 2S LiPo (7.4V) requires a voltage regulator to step down to 3.7V for the motors.
> The DRV8833 is a MOSFET-based driver with minimal voltage drop (~0.2V), much better than L298N (~2V drop).

## Frame Dimensions

| Dimension | Value |
|-----------|-------|
| Body Size | 95 x 75 x 4 mm |
| Arm Length | 65mm (mount to motor) |
| Motor Diagonal | ~90mm from center |
| Prop Guard ID | 75mm |
| Total Span | ~250mm diagonal |

## Parts List

| Part | Quantity | Description |
|------|----------|-------------|
| frame_body | 1 | Central body with mounting points |
| frame_arm | 4 | Motor mount arms |
| prop_guard | 4 | Propeller protection cages |
| battery_cover | 1 | LiPo battery protection |

## Weight Budget

| Component | Weight | Qty | Total |
|-----------|--------|-----|-------|
| Motors (820 brushed) | 5g | 4 | 20g |
| Battery (2S 300-500mAh) | ~25g | 1 | 25g |
| Arduino R4 WiFi | ~10g | 1 | 10g |
| MPU6050 | 4g | 1 | 4g |
| DRV8833 driver | ~1g | 2 | 2g |
| Voltage regulator | ~2g | 1 | 2g |
| Frame (PLA) | ~20g | - | 20g |
| Props + wires | ~10g | - | 10g |
| **TOTAL** | | | **~93g** |

> Using 2× DRV8833 instead of L298N saves ~31g - significant for a micro drone.

## Print Settings

### Recommended Settings

| Setting | Value |
|---------|-------|
| Layer Height | 0.2mm |
| Nozzle | 0.4mm |
| Infill | 15-20% Gyroid |
| Walls | 3 (1.2mm) |
| Top/Bottom | 4 layers |
| Material | PLA or PETG |

### Part-Specific Notes

**Frame Body:**
- Print flat side down
- Supports not needed
- Consider 25% infill for arm mounts

**Frame Arms:**
- Print with mounting plate down
- May need supports for motor socket
- Use 20% infill for strength

**Prop Guards:**
- Print with lower ring down
- No supports needed
- Can use 15% infill

**Battery Cover:**
- Print with flat side down
- No supports needed
- 15% infill sufficient

## Assembly Order

1. Print all parts
2. Insert motors into arm sockets (press-fit, 8.2mm socket for 8mm motor)
3. Mount arms to body using M3x10 screws
4. Push prop guards onto motor mounts (friction-fit sleeve)
5. Mount Arduino R4 WiFi to standoffs (M3x6 screws)
6. Mount MPU6050 to center platform (M2.5 screws + vibration dampeners)
7. Mount DRV8833 driver on body (double-sided tape or small screws)
8. Wire motors to DRV8833, DRV8833 to Arduino
9. Connect voltage regulator (7.4V → 3.7V for motors)
10. Place battery in compartment
11. Attach battery cover (slides onto rails)

## Hardware Required

| Item | Quantity | Notes |
|------|----------|-------|
| M3 screws | 16 | M3x10mm (arms to body) |
| M3 screws | 4 | M3x6mm (Arduino standoffs) |
| M2.5 screws | 4 | M2.5x6mm (IMU mount) |
| M3 nuts | 8 | Standard |
| Vibration dampeners | 4 | For IMU |
| Battery strap | 1 | 10mm wide |
| Voltage regulator | 1 | 7.4V → 3.7V (for motors) |
| DRV8833 motor driver | 2 | 18×12mm module (pack of 2) |

## File Formats

After running `export_all.py`:

| Format | Use |
|--------|-----|
| `.stl` | 3D printing (slicer import) |
| `.step` | CAD editing |
| `.glb` | Web viewing |

## Export Files

Run the export script to generate all output files:

```bash
cd D:\Src\drone
python 3d-parts/export_all.py
```

Exports are saved to the project `/build` directory.
Then open `build/viewer.html` in a browser to preview.

## Design Considerations

### Center of Mass

The IMU (MPU6050) is positioned at the geometric center for accurate flight control:

```
Top View:
     [Motor]           [Motor]
         \             /
          \  Arduino  /
           \_________/
           |   IMU   |  <- Geometric center
           |  (CG)   |
           |_________|
          /   LiPo   \
         /  (below)   \
     [Motor]           [Motor]
```

The battery is placed below center to lower the center of gravity.

### Motor Specifications

**820 Coreless Brushed Motors:**
- Dimensions: 8mm diameter × 20mm length
- Shaft: 1.0mm diameter, 7.5mm length
- Voltage: DC 3.7V (1S LiPo equivalent)
- RPM: 43,000-50,000 RPM
- Weight: ~5g each
- Compatible Props: 55-75mm

### Motor Driver - DRV8833

**Why DRV8833 over L298N:**

| Feature | DRV8833 | L298N |
|---------|---------|-------|
| Voltage drop | ~0.2V | ~2V |
| Size | 18×12mm | 55×49mm |
| Weight | ~1g | ~33g |
| Efficiency | High (MOSFET) | Low (BJT) |
| Motor voltage | 3.5V delivered | 1.7V delivered* |

*With 3.7V input to L298N, motors only get ~1.7V after the 2V drop.

**DRV8833 Specs:**
- 2 H-bridge channels per board
- 1.5A continuous per channel (2A peak)
- Operating voltage: 2.7V - 10.8V
- PWM frequency: up to 250kHz
- Built-in overcurrent protection

**Wiring for 4 motors (2 boards needed):**
```
DRV8833 #1 (Front):        DRV8833 #2 (Rear):
  OUT1 → Motor 1 (FR)        OUT1 → Motor 3 (RL)
  OUT2 → Motor 2 (FL)        OUT2 → Motor 4 (RR)

Both boards share:
  VCC → 3.7V (from regulator)
  GND → Common ground
  IN1-IN4 → Arduino PWM pins
```

### Propeller Clearance

- Prop diameter: 63.5mm
- Safety clearance: 5mm each side
- Guard internal diameter: 75mm

### Weight Optimization

- Triangular truss pattern in body (10mm triangles, 3mm walls) - stronger than honeycomb
- Weight reduction slots in arms
- Open-cage prop guards for airflow
- Target frame weight: 20g

### Strength vs Weight Trade-off

The frame uses a **triangular truss pattern** instead of hexagonal honeycomb:
- Triangles are inherently rigid shapes
- 3mm walls provide crash resistance
- Pattern avoids all mounting points and critical areas
- ~40% lighter than solid while maintaining structural integrity
