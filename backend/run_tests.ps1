# Get Venv Python (reuse logic simplistic)
$VENV_PYTHON = "venv\Scripts\python.exe"
if (-not (Test-Path $VENV_PYTHON)) {
    Write-Error "Virtual environment not found. Run run_server.ps1 first."
    exit 1
}

# Run Test
Write-Host "Running API Test..."
& $VENV_PYTHON scripts/test_api.py
