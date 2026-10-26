$ErrorActionPreference = 'Stop'
Write-Host 'AskAbhi 360 - local launch helper' -ForegroundColor Green
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    py -3.11 -m venv .venv
}
$py = Resolve-Path '.venv\Scripts\python.exe'
Write-Host 'Installing/checking required packages...' -ForegroundColor Cyan
& $py -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed. Read the pip error above.' }
Write-Host 'Compiling app and source files...' -ForegroundColor Cyan
& $py -m compileall -q app.py config.py core ui scripts tests
if ($LASTEXITCODE -ne 0) { throw 'Python compilation failed.' }
Write-Host 'Running tests...' -ForegroundColor Cyan
& $py -m pytest -q
if ($LASTEXITCODE -ne 0) { throw 'Automated tests failed. Read the pytest output above.' }
Write-Host 'Starting AskAbhi 360...' -ForegroundColor Green
& $py -m streamlit run app.py
