param([switch]$Desktop)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $projectRoot
$portableNode = Join-Path $projectRoot '.tools\node-v22.16.0-win-x64'
if (Test-Path $portableNode) { $env:PATH = "$portableNode;$env:PATH" }
$env:CARGO_HOME = Join-Path $projectRoot '.tools\cargo'
$env:RUSTUP_HOME = Join-Path $projectRoot '.tools\rustup'
if (Test-Path "$env:CARGO_HOME\bin") { $env:PATH = "$env:CARGO_HOME\bin;$env:PATH" }
if (!(Test-Path '.venv\Scripts\python.exe')) { throw 'Bitte zuerst scripts/setup.ps1 ausführen.' }
if (!(Test-Path 'dist\index.html') -and !$Desktop) { & npm.cmd run build; if ($LASTEXITCODE) { throw 'Frontend build failed' } }
if ($Desktop) {
    $service = $null
    try {
        try { $health = Invoke-RestMethod 'http://127.0.0.1:8765/api/health' -TimeoutSec 3 } catch { $health = $null }
        if (!$health) {
            $service = Start-Process -FilePath "$projectRoot\.venv\Scripts\python.exe" -ArgumentList '-m','uvicorn','backend.app:app','--host','127.0.0.1','--port','8765' -WorkingDirectory $projectRoot -PassThru -WindowStyle Hidden
            for ($attempt=0; $attempt -lt 30; $attempt++) {
                try { $health = Invoke-RestMethod 'http://127.0.0.1:8765/api/health' -TimeoutSec 2; break } catch { Start-Sleep -Milliseconds 500 }
            }
            if (!$health) { throw 'Backend konnte nicht gestartet werden.' }
        }
        if ($health.status -ne 'ok' -or $health.version -ne '0.3.0' -or $health.api_revision -ne 3) {
            throw 'Unpassendes Backend auf Port 8765. Bisherigen MoodScope-Dienst beenden und erneut starten.'
        }
        $nativeApp = @('src-tauri\target\v03\release\moodscope.exe','src-tauri\target\v02\release\moodscope.exe','src-tauri\target\release\moodscope.exe') | Where-Object { Test-Path $_ } | Get-Item | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($nativeApp) {
            Start-Process -FilePath $nativeApp.FullName -WorkingDirectory $projectRoot -Wait -WindowStyle Normal
        } else { & npm.cmd run tauri dev }
    } finally { if ($service) { Stop-Process -Id $service.Id -ErrorAction SilentlyContinue } }
} else {
    Write-Host 'MoodScope: http://127.0.0.1:8765 (im Browser öffnen). Mit Strg+C beenden.'
    & .venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8765
}
