param([switch]$Live)
$ErrorActionPreference = 'Stop'
$b4Root = Split-Path -Parent $PSScriptRoot
$b4Python = 'C:\Users\32433\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (-not (Test-Path -LiteralPath $b4Python)) { throw 'Configured Python currently not discoverable; inspect existing interpreter locations before installing.' }
$env:PYTHONPATH = (Join-Path $b4Root 'work\b4-python-deps') + ';' + (Join-Path $b4Root 'src') + ';' + $b4Root + ';' + $env:PYTHONPATH
$env:PYTHONUTF8 = '1'
Push-Location $b4Root
try {
    if ($Live) { & $b4Python scripts/b4_experiments.py --live }
    else { & $b4Python scripts/b4_experiments.py }
    if ($LASTEXITCODE -ne 0) { throw "B4 verification exited $LASTEXITCODE" }
} finally { Pop-Location }
