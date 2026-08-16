$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$dest = Join-Path $env:USERPROFILE ".claude\skills"
New-Item -ItemType Directory -Force -Path $dest | Out-Null

Get-ChildItem -Directory $root | ForEach-Object {
    if ($_.Name -eq ".git") { return }
    $target = Join-Path $dest $_.Name
    Remove-Item -Recurse -Force $target -ErrorAction SilentlyContinue
    Copy-Item -Recurse -Force $_.FullName $target
    Write-Output "installed: $target"
}
Write-Output "Done. Restart Claude Code to load the skills."
