$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$dest = Join-Path $env:USERPROFILE ".claude\skills"
New-Item -ItemType Directory -Force -Path $dest | Out-Null

Get-ChildItem -Directory (Join-Path $root "skills") | ForEach-Object {
    # Only install skill directories (those with a SKILL.md).
    if (-not (Test-Path (Join-Path $_.FullName "SKILL.md"))) { return }
    $target = Join-Path $dest $_.Name
    Remove-Item -Recurse -Force $target -ErrorAction SilentlyContinue
    Copy-Item -Recurse -Force $_.FullName $target
    Write-Output "installed: $target"
}
Write-Output "Done. Restart Claude Code to load the skills."
