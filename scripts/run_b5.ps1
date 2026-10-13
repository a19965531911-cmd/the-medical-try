param([string]$Endpoint='http://127.0.0.1:1213/v1/chat/completions',[string]$Model='local-model',[switch]$SkipRegression)
$ErrorActionPreference='Stop'
$b5Root=Split-Path -Parent $PSScriptRoot
$b5Python='C:\Users\32433\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if(-not(Test-Path -LiteralPath $b5Python)){throw 'Configured interpreter currently not discoverable; inspect existing environments first.'}
$env:PYTHONPATH=(Join-Path $b5Root 'work\b4-python-deps')+';'+(Join-Path $b5Root 'src')+';'+$b5Root+';'+$env:PYTHONPATH
$env:PYTHONUTF8='1'
Push-Location $b5Root
try{
    $b5Args=@('scripts/b5_experiments.py','--endpoint',$Endpoint,'--model',$Model)
    if($SkipRegression){$b5Args+='--skip-regression'}
    & $b5Python @b5Args
    if($LASTEXITCODE -ne 0){throw "B5 audit exited $LASTEXITCODE"}
}finally{Pop-Location}
