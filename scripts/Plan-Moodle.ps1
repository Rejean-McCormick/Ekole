$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path "$PSScriptRoot\..")
py -3 tools\ekole.py moodle-plan
if ($LASTEXITCODE -ne 0) { throw "Plan Moodle failed" }
