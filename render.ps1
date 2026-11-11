# Render a scene inside Docker (Windows PowerShell).
#   .\render.ps1 <file.py> <SceneClass> [low|hd]
# low (default) = 480p30 preview, hd = 1080p60. Output: media/<SceneClass>.mp4
param(
    [Parameter(Mandatory = $true, Position = 0)][string]$File,
    [Parameter(Mandatory = $true, Position = 1)][string]$SceneClass,
    [Parameter(Position = 2)][ValidateSet("low", "hd")][string]$Quality = "low"
)
Set-Location $PSScriptRoot

if ($Quality -eq "hd") { $qargs = @("-w", "--hd", "--config_file", "hd60_config.yml") }
else { $qargs = @("-w", "-l") }

docker compose run --rm manim $File $SceneClass @qargs --video_dir media
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not (Test-Path "media/$SceneClass.mp4") -or (Get-Item "media/$SceneClass.mp4").Length -eq 0) {
    Write-Error "media/$SceneClass.mp4 was not created"
    exit 1
}
Write-Host "OK: media/$SceneClass.mp4"
