$ErrorActionPreference='Stop'
$b5Root=Split-Path -Parent $PSScriptRoot
$b5Exe='D:\DeepTutor\ollama\ollama.exe'
$b5Models='D:\DeepTutor\ollama-models'
if(-not(Test-Path -LiteralPath $b5Exe)){throw 'Existing trusted Ollama executable currently not discoverable.'}
if(-not(Test-Path -LiteralPath (Join-Path $b5Models 'manifests'))){throw 'Existing local model manifest directory not found.'}
& $b5Exe --version
if($LASTEXITCODE -ne 0){throw 'Ollama absolute-path version validation failed.'}
if(Get-NetTCPConnection -LocalPort 11434 -State Listen -ErrorAction SilentlyContinue){throw '11434 already listening; inspect that existing service instead of starting another.'}
$b5Logs=Join-Path $b5Root 'experiment\b5'
New-Item -ItemType Directory -Path $b5Logs -Force | Out-Null
$env:OLLAMA_HOST='127.0.0.1:11434'
$env:OLLAMA_MODELS=$b5Models
$env:OLLAMA_NO_CLOUD='1'
$env:OLLAMA_NOPRUNE='1'
$b5Process=Start-Process -FilePath $b5Exe -ArgumentList 'serve' -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $b5Logs 'ollama.stdout.log') -RedirectStandardError (Join-Path $b5Logs 'ollama.stderr.log')
Write-Output "Existing local Ollama started, PID=$($b5Process.Id). No model download. Run b5_model_environment.py to verify capabilities."
