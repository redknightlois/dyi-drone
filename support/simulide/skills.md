# SimulIDE Installation

## Overview

SimulIDE is a real-time electronic circuit simulator supporting PIC, AVR, and Arduino. This guide covers downloading and installing from scratch.

## Download

### Official Sources

- **Direct Download**: https://simulide.com/p/direct_downloads/SimulIDE_1.1.0-SR1_Win64.zip
- **Official Website**: https://simulide.com/p/downloads/
- **GitHub**: https://github.com/SimulIDE/SimulIDE

### Download Steps (Windows)

#### Option A: Run Install Script (Recommended)

Run the included installation script:

```powershell
.\install.ps1
```

Or from any directory:
```powershell
D:\Src\drone\support\simulide\install.ps1
```

#### Option B: Manual Download

1. Download from: https://simulide.com/p/direct_downloads/SimulIDE_1.1.0-SR1_Win64.zip
2. Extract to this directory (`D:\Src\drone\support\simulide\`)

#### Option C: Using curl (Git Bash / WSL)

```bash
INSTALL_DIR="D:/Src/drone/support/simulide"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

curl -L -o simulide.zip "https://simulide.com/p/direct_downloads/SimulIDE_1.1.0-SR1_Win64.zip"
unzip -o simulide.zip
rm simulide.zip

# Move contents from nested folder if exists
NESTED=$(find . -maxdepth 1 -type d -name "SimulIDE*" | head -1)
if [ -n "$NESTED" ]; then
    mv "$NESTED"/* ./
    rmdir "$NESTED"
fi
```

## Contents After Installation

- `simulide.exe` - The main executable
- `data/` - Application data and resources
- `examples/` - Example circuit files

## Setup

### Create Desktop Shortcut (Optional)

**Windows (PowerShell):**
```powershell
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\SimulIDE.lnk")
$Shortcut.TargetPath = "D:\Src\drone\support\simulide\simulide.exe"
$Shortcut.WorkingDirectory = "D:\Src\drone\support\simulide"
$Shortcut.Save()
```

### Add to PATH (Optional)

**Windows (PowerShell - Admin):**
```powershell
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
$newPath = "D:\Src\drone\support\simulide"
[Environment]::SetEnvironmentVariable("Path", "$currentPath;$newPath", "Machine")
```

## Verification

Launch SimulIDE:

```bash
D:\Src\drone\support\simulide\simulide.exe
```

Or if added to PATH:
```bash
simulide.exe
```

## Usage with Drone Firmware

### Workflow

1. Compile firmware with arduino-cli:
   ```bash
   arduino-cli compile --fqbn arduino:avr:mega D:\Src\drone
   ```

2. Open SimulIDE

3. Create or open a circuit with an Arduino Mega component

4. Right-click the microcontroller → "Load firmware"

5. Navigate to the compiled `.hex` file:
   ```
   D:\Src\drone\build\arduino.avr.mega\firmware.ino.hex
   ```

6. Start the simulation

## Troubleshooting

- **Missing DLLs**: Install Visual C++ Redistributable (https://aka.ms/vs/17/release/vc_redist.x64.exe)
- **Simulation runs slowly**: Reduce circuit complexity or simulation speed
- **Firmware not loading**: Verify the `.hex` file path and that compilation succeeded
- **Components not responding**: Check virtual wire connections in the circuit
- **Download fails from SourceForge**: Try the direct link from https://simulide.com/p/downloads/
