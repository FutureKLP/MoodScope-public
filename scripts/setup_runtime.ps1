param([switch]$Cpu)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $projectRoot
$pythonRoot = Join-Path $projectRoot '.tools\python313'
$portablePython = Join-Path $pythonRoot 'tools\python.exe'
if (!(Test-Path -LiteralPath $portablePython)) {
    New-Item -ItemType Directory -Force -Path '.tools' | Out-Null
    $archive = Join-Path $projectRoot '.tools\python313.zip'
    Invoke-WebRequest 'https://api.nuget.org/v3-flatcontainer/python/3.13.17/python.3.13.17.nupkg' -OutFile $archive
    $pythonHash = 'dce409744b088f94c6e37ba41f8100c384c27e029e843237364c602d30d475e5'
    if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $pythonHash) { throw 'Python package checksum mismatch.' }
    Expand-Archive -LiteralPath $archive -DestinationPath $pythonRoot -Force
}
if (!(Test-Path '.venv-modern\Scripts\python.exe')) {
    & $portablePython -m venv .venv-modern
    if ($LASTEXITCODE) { throw 'Project environment creation failed.' }
}
$projectPython = Join-Path $projectRoot '.venv-modern\Scripts\python.exe'
$marker = Join-Path $projectRoot '.venv-modern\.moodscope-validated'
if (Test-Path -LiteralPath $marker) { Remove-Item -LiteralPath $marker }
& $projectPython -m pip install --upgrade pip
if ($LASTEXITCODE) { throw 'pip update failed.' }
if (!$Cpu) {
    & $projectPython -m pip install 'https://download-r2.pytorch.org/whl/cu132/torch-2.15.0%2Bcu132-cp313-cp313-win_amd64.whl#sha256=7b54774dedca2a1147f1ae47451d9a8a7e88b80665fc505bf6a4f1f427d21e97'
    if ($LASTEXITCODE) { throw 'CUDA PyTorch installation failed; use -Cpu for a CPU environment.' }
}
& $projectPython -m pip install -r backend/requirements.txt -r backend/requirements-separation.txt
if ($LASTEXITCODE) { throw 'Python dependencies failed.' }
if (!$Cpu) {
    & $projectPython -m pip install -r backend/requirements-whisper-cuda.txt
    if ($LASTEXITCODE) { throw 'Whisper CUDA dependencies failed.' }
}
& $projectPython -m pip check
if ($LASTEXITCODE) { throw 'Dependency compatibility check failed.' }
& $projectPython -c 'import torch, transformers, faster_whisper, demucs; print(''Python runtime imports passed'')'
if ($LASTEXITCODE) { throw 'Runtime import check failed.' }
if (!$Cpu) {
    & $projectPython -c 'import torch; assert torch.cuda.is_available(); print((torch.ones(4, device=''cuda'') * 2).sum().item())'
    if ($LASTEXITCODE) { throw 'CUDA kernel check failed; driver/CUDA compatibility must be resolved before activation.' }
}
Set-Content -LiteralPath $marker -Value 'Python 3.13 project runtime validated' -Encoding ascii
Write-Host 'Project-local runtime ready. No system Python or GPU driver was installed.'
