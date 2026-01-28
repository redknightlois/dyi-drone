# Prerequisites

## Required Tools

### Arduino CLI

Command-line tool for compiling and uploading Arduino firmware.

**Installation:**
```powershell
.\support\arduino-cli\install.ps1
```

**Post-installation setup:**
```bash
arduino-cli config init
arduino-cli core update-index
arduino-cli core install arduino:avr
```

**Verification:**
```bash
arduino-cli version
```

### SimulIDE (Optional)

Real-time electronic circuit simulator for testing without hardware.

**Installation:**
```powershell
.\support\simulide\install.ps1
```

**Launch:**
```
.\support\simulide\simulide.exe
```

## Installation Locations

After running the install scripts, tools are located at:

| Tool | Path |
|------|------|
| arduino-cli | `support\arduino-cli\arduino-cli.exe` |
| SimulIDE | `support\simulide\simulide.exe` |

## Detailed Documentation

For more options and troubleshooting, see:

- `support\arduino-cli\skills.md`
- `support\simulide\skills.md`
