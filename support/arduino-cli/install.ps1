# Arduino CLI Installation Script
# Downloads and installs Arduino CLI to this directory

$ErrorActionPreference = "Stop"
$installDir = $PSScriptRoot

Write-Host "Arduino CLI Installation Script" -ForegroundColor Cyan
Write-Host "Install directory: $installDir"
Write-Host ""

# Check if already installed
if (Test-Path "$installDir\arduino-cli.exe") {
    Write-Host "Arduino CLI is already installed." -ForegroundColor Yellow
    $response = Read-Host "Reinstall? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "Installation cancelled."
        exit 0
    }
}

# Get latest release info from GitHub API
Write-Host "Fetching latest version info..." -ForegroundColor Green
$releaseInfo = Invoke-RestMethod -Uri "https://api.github.com/repos/arduino/arduino-cli/releases/latest"
$version = $releaseInfo.tag_name -replace "^v", ""

# Find Windows 64-bit asset
$asset = $releaseInfo.assets | Where-Object { $_.name -like "*Windows_64bit.zip" }
$downloadUrl = $asset.browser_download_url

Write-Host "Downloading Arduino CLI $version..." -ForegroundColor Green
$zipPath = "$installDir\arduino-cli.zip"
Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath

# Extract
Write-Host "Extracting..." -ForegroundColor Green
Expand-Archive -Path $zipPath -DestinationPath $installDir -Force
Remove-Item $zipPath

# Verify installation
if (Test-Path "$installDir\arduino-cli.exe") {
    Write-Host ""
    Write-Host "Arduino CLI $version installed successfully!" -ForegroundColor Green
    Write-Host "Location: $installDir\arduino-cli.exe"
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Add to PATH or run from this directory"
    Write-Host "  2. Run: arduino-cli config init"
    Write-Host "  3. Run: arduino-cli core update-index"
    Write-Host "  4. Run: arduino-cli core install arduino:avr"
} else {
    Write-Host "Installation may have failed. Please check the directory." -ForegroundColor Red
    exit 1
}
