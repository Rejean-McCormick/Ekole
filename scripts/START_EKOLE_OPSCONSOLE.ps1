# Ekole OpsConsole — aucun script externe ni elevation requise.
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location -LiteralPath $RepoRoot
if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 (Join-Path $RepoRoot 'opsconsole\ekole_ops.py')
}
elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python (Join-Path $RepoRoot 'opsconsole\ekole_ops.py')
}
else { throw 'Python 3 introuvable dans le PATH.' }
