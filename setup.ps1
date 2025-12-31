# Setup script for truck-inspection PoC
# Run from PowerShell in project folder

# 1) Create virtual environment
python -m venv .venv

# 2) Activate (PowerShell)
. .\.venv\Scripts\Activate.ps1

# 3) Upgrade pip and install dependencies
python -m pip install -U pip
pip install -r requirements.txt

# 4) Create outputs and data folders (if not existing)
if (-not (Test-Path data)) { New-Item -ItemType Directory -Path data }
if (-not (Test-Path outputs)) { New-Item -ItemType Directory -Path outputs }

# 5) Download sample images for demo
Invoke-WebRequest -Uri https://ultralytics.com/images/zidane.jpg -OutFile data\sample1.jpg -UseBasicParsing
Invoke-WebRequest -Uri https://raw.githubusercontent.com/opencv/opencv/master/samples/data/opencv-logo.png -OutFile data\template.png -UseBasicParsing

Write-Host "Setup complete. Activate the venv with: . .\\.venv\\Scripts\\Activate.ps1" -ForegroundColor Green
