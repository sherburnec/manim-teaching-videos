# Inspect a rendered video (Windows PowerShell): prints resolution, fps,
# duration, size, and writes media/<SceneClass>_contact.png (grid of stills).
#   .\check.ps1 <SceneClass>
param([Parameter(Mandatory = $true, Position = 0)][string]$SceneClass)
Set-Location $PSScriptRoot

$video = "media/$SceneClass.mp4"
if (-not (Test-Path $video)) { Write-Error "$video not found"; exit 1 }

docker compose run --rm -T --entrypoint ffprobe manim -v error `
    -show_entries "stream=width,height,r_frame_rate:format=duration,size" `
    -of default=nw=1 $video

docker compose run --rm -T --entrypoint ffmpeg manim -y -v error -i $video `
    -vf "fps=1/2.2,scale=427:-1,tile=4x3" -frames:v 1 "media/${SceneClass}_contact.png"
Write-Host "Contact sheet: media/${SceneClass}_contact.png"
