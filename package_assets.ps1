param(
    [switch]$Sync,
    [switch]$CheckOnly
)

$ErrorActionPreference = "Stop"
$arguments = @()
if ($Sync) { $arguments += "--sync" }
$arguments += "--check"
if (-not $CheckOnly) { $arguments += "--build" }

& python (Join-Path $PSScriptRoot "tools\assemble_assets.py") @arguments
exit $LASTEXITCODE
