$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path "$PSScriptRoot\..")
py -3 tools\ekole.py verify
if ($LASTEXITCODE -ne 0) { throw "Validation Ekole failed" }
