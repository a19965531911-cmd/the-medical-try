param([ValidateSet('FAST','INTEGRATION','STRESS','FULL')][string]$Group='FAST')
$b72Root=Split-Path -Parent $PSScriptRoot
$b72Python='C:\Users\32433\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$env:PYTHONPATH=(Join-Path $b72Root 'work\b6-python-deps')+';'+(Join-Path $b72Root 'work\b4-python-deps')+';'+(Join-Path $b72Root 'src')+';'+$b72Root+';'+$env:PYTHONPATH
$env:PYTHONUTF8='1'
Push-Location $b72Root
try {
    $b72Tests=@()
    if($Group -eq 'FAST'){$b72Tests=@('tests/b_board/test_b7_2.py','tests/b_board/test_b7_1.py','tests/b_board/test_b7_schema.py')}
    if($Group -eq 'STRESS'){$b72Tests=@('tests/b_board/test_b6_http.py')}
    if($Group -eq 'INTEGRATION'){& $b72Python scripts/b7_2_experiments.py}
    else{& $b72Python -m pytest @b72Tests -q -o cache_dir=work/b72-cache --durations=20}
    if($LASTEXITCODE -ne 0){throw "B7.2 $Group exited $LASTEXITCODE"}
}finally{Pop-Location}
