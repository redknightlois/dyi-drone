# SimulIDE Installation Script
# Downloads and installs SimulIDE to this directory

$ErrorActionPreference = "Stop"
$installDir = $PSScriptRoot

Write-Host "SimulIDE Installation Script" -ForegroundColor Cyan
Write-Host "Install directory: $installDir"
Write-Host ""

# Check if already installed
if (Test-Path "$installDir\simulide.exe") {
    Write-Host "SimulIDE is already installed." -ForegroundColor Yellow
    $response = Read-Host "Reinstall? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "Installation cancelled."
        exit 0
    }
}

# Download
$version = "1.1.0"
$release = "SR1"
$downloadUrl = "https://simulide.com/p/direct_downloads/SimulIDE_${version}-${release}_Win64.zip"
$zipPath = "$installDir\simulide.zip"

Write-Host "Downloading SimulIDE $version-$release..." -ForegroundColor Green
Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath

# Extract
Write-Host "Extracting..." -ForegroundColor Green
Expand-Archive -Path $zipPath -DestinationPath $installDir -Force
Remove-Item $zipPath

# Move contents from nested folder if exists
$nestedDir = Get-ChildItem -Path $installDir -Directory | Where-Object { $_.Name -like "SimulIDE*" } | Select-Object -First 1
if ($nestedDir) {
    Write-Host "Organizing files..."
    Get-ChildItem -Path $nestedDir.FullName | Move-Item -Destination $installDir -Force
    Remove-Item $nestedDir.FullName -Recurse -Force
}

# Verify installation
if (Test-Path "$installDir\simulide.exe") {
    Write-Host ""
    Write-Host "SimulIDE $version-$release installed successfully!" -ForegroundColor Green
    Write-Host "Location: $installDir\simulide.exe"
} else {
    Write-Host "Installation may have failed. Please check the directory." -ForegroundColor Red
    exit 1
}
