# Drone Firmware

## Project Overview

Arduino-based drone firmware for Arduino R4 WiFi with MPU6050 IMU and DRV8833 motor drivers. Includes 3D-printable frame designs using build123d.

## Build & Test

```bash
arduino-cli compile --fqbn arduino:avr:mega .
arduino-cli upload -p COM3 --fqbn arduino:avr:mega .
```

## Skills

Project skills live in `support/skills/` and are discovered via symlinks in `.claude/skills/` and `.agents/skills/`.

To install skill symlinks:
- **WSL/Linux/macOS:** `./ensure-skills.sh`
- **Windows (PowerShell):** `.\ensure-skills.ps1`

The script is idempotent — safe to run repeatedly.

## Conventions

- Code is written in English; documentation may be in Spanish
- Use `build123d` for 3D part design (scripts in `3d-parts/`)
- Export 3D files with `python 3d-parts/export_all.py`
