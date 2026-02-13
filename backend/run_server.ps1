# Function to find best python
function Get-PythonPath {
    $versions = "3.10", "3.11", "3.12"
    foreach ($v in $versions) {
        if (Get-Command "py" -ErrorAction SilentlyContinue) {
            try {
                $path = py -$v -c "import sys; print(sys.executable)" 2>$null
                if ($path) { return $path }
            } catch {}
        }
    }
    # Fallback to system python
    return (Get-Command "python" -ErrorAction SilentlyContinue).Source
}

$PYTHON = Get-PythonPath

if (-not $PYTHON) {
    Write-Error "No Python found! Please install Python 3.10-3.12."
    exit 1
}

Write-Host "Using Python: $PYTHON"

# Verify Version logic (strict for paddle)
& $PYTHON -c "import sys; v=sys.version_info; print(f'Version: {v.major}.{v.minor}'); sys.exit(0 if v.major == 3 and v.minor <= 12 else 1)"
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Detected Python version might be incompatible with PaddleOCR (Requires <= 3.12)."
}

# Create venv if not exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    & $PYTHON -m venv venv
}

# Determine venv python path 
$VENV_PYTHON = "$PSScriptRoot\venv\Scripts\python.exe"

if (-not (Test-Path $VENV_PYTHON)) {
    Write-Error "Virtual environment creation failed or python.exe not found in venv."
    exit 1
}

# Upgrade pip
Write-Host "Upgrading pip..."
& $VENV_PYTHON -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing dependencies..."
# Separate complex installs
& $VENV_PYTHON -m pip install paddlepaddle paddleocr
& $VENV_PYTHON -m pip install -r requirements.txt

# Start Server
Write-Host "Starting Server..."
$env:PYTHONPATH = "."
& $VENV_PYTHON -m uvicorn app.main:app --reload
