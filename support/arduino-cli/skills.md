# Arduino CLI Installation

## Overview

Arduino CLI is a command-line tool for compiling and uploading Arduino firmware. This guide covers downloading and installing from scratch.

## Download

### Official Sources

- **GitHub Releases (Recommended)**: https://github.com/arduino/arduino-cli/releases
- **Official Documentation**: https://docs.arduino.cc/arduino-cli/installation

### Download Steps (Windows)

#### Option A: Run Install Script (Recommended)

Run the included installation script:

```powershell
.\install.ps1
```

Or from any directory:
```powershell
D:\Src\drone\support\arduino-cli\install.ps1
```

#### Option B: Manual Download

1. Go to https://github.com/arduino/arduino-cli/releases
2. Find the latest release
3. Download `arduino-cli_<version>_Windows_64bit.zip`
4. Extract to this directory (`D:\Src\drone\support\arduino-cli\`)

#### Option C: PowerShell Script (Inline)

```powershell
# Create directory if it doesn't exist
$installDir = "D:\Src\drone\support\arduino-cli"
New-Item -ItemType Directory -Force -Path $installDir | Out-Null

# Get latest release info from GitHub API
$releaseInfo = Invoke-RestMethod -Uri "https://api.github.com/repos/arduino/arduino-cli/releases/latest"
$version = $releaseInfo.tag_name -replace '^v', ''

# Find Windows 64-bit asset
$asset = $releaseInfo.assets | Where-Object { $_.name -like "*Windows_64bit.zip" }
$downloadUrl = $asset.browser_download_url

# Download and extract
$zipPath = "$installDir\arduino-cli.zip"
Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath
Expand-Archive -Path $zipPath -DestinationPath $installDir -Force
Remove-Item $zipPath

Write-Host "Arduino CLI $version installed to $installDir"
```

#### Option D: Using curl (Git Bash / WSL)

```bash
INSTALL_DIR="D:/Src/drone/support/arduino-cli"
mkdir -p "$INSTALL_DIR"

# Get latest version
VERSION=$(curl -s https://api.github.com/repos/arduino/arduino-cli/releases/latest | grep -Po '"tag_name": "\Kv[^"]*')

# Download and extract
curl -L "https://github.com/arduino/arduino-cli/releases/download/${VERSION}/arduino-cli_${VERSION#v}_Windows_64bit.zip" -o arduino-cli.zip
unzip -o arduino-cli.zip -d "$INSTALL_DIR"
rm arduino-cli.zip
```

#### Option E: Chocolatey (if installed)

```cmd
choco install arduino-cli
```

## Contents After Installation

- `arduino-cli.exe` - The main executable
- `LICENSE.txt` - License information

## Setup

### Add to PATH (Recommended)

**Windows (PowerShell - Admin):**
```powershell
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
$newPath = "D:\Src\drone\support\arduino-cli"
[Environment]::SetEnvironmentVariable("Path", "$currentPath;$newPath", "Machine")
```

**Windows (CMD - Admin):**
```cmd
setx PATH "%PATH%;D:\Src\drone\support\arduino-cli" /M
```

### Initialize Arduino CLI

After installation, initialize configuration and install required cores:

```bash
arduino-cli config init
arduino-cli core update-index
arduino-cli core install arduino:avr
```

## Verification

```bash
arduino-cli version
arduino-cli board list
```

## Common Commands

| Command | Description |
|---------|-------------|
| `arduino-cli compile --fqbn arduino:avr:mega .` | Compile for Arduino Mega |
| `arduino-cli upload -p COM3 --fqbn arduino:avr:mega .` | Upload to device |
| `arduino-cli board list` | List connected boards |
| `arduino-cli monitor -p COM3` | Open serial monitor |
| `arduino-cli lib search <name>` | Search libraries |
| `arduino-cli lib install <name>` | Install library |

## Troubleshooting

- **Board not detected**: Install appropriate USB drivers for your board
- **Permission denied**: Run terminal as Administrator
- **Core not found**: Run `arduino-cli core update-index` first
- **Download fails**: Check internet connection and firewall settings
