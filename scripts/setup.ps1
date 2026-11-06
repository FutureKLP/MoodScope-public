$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$portableNode = Join-Path $PWD '.tools\node-v22.16.0-win-x64'
if (Test-Path $portableNode) { $env:PATH = "$portableNode;$env:PATH" }
if (!(Get-Command node -ErrorAction SilentlyContinue)) { throw 'Node.js 22+ benötigt. Keine automatische systemweite Installation.' }
& (Join-Path $PSScriptRoot 'setup_runtime.ps1')
if ($LASTEXITCODE) { throw 'Python setup failed' }
& npm.cmd ci
if ($LASTEXITCODE) { throw 'Node setup failed' }
& npm.cmd run build
if ($LASTEXITCODE) { throw 'Build failed' }
