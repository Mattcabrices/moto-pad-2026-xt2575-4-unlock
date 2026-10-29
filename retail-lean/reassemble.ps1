$ErrorActionPreference = 'Stop'
$releaseDir = $PSScriptRoot
$manifest = Get-Content -LiteralPath (Join-Path $releaseDir 'BUILD-MANIFEST.json') -Raw | ConvertFrom-Json
function ReleasePath([string]$name) {
    if ([IO.Path]::GetFileName($name) -ne $name -or $name -in @('.', '..')) { throw 'Unsafe filename in manifest' }
    return Join-Path $releaseDir $name
}
function CheckFile($entry) {
    $path = ReleasePath $entry.filename
    $file = Get-Item -LiteralPath $path
    if ($file.Length -ne $entry.bytes) { throw "Wrong file size: $($entry.filename)" }
    $actual = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $entry.sha256) { throw "Checksum mismatch: $($entry.filename)" }
}
foreach ($image in $manifest.images) {
    if ($image.parts) {
        foreach ($part in $image.parts) { CheckFile $part }
        $output = ReleasePath $image.filename
        if (-not (Test-Path -LiteralPath $output)) {
            $destination = [IO.File]::Open($output, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write)
            try {
                foreach ($part in $image.parts) {
                    $source = [IO.File]::OpenRead((ReleasePath $part.filename))
                    try { $source.CopyTo($destination) } finally { $source.Dispose() }
                }
            } finally { $destination.Dispose() }
        }
    }
    CheckFile $image
    Write-Output "Verified $($image.filename)"
}
Write-Output 'All four images verified. This script does not flash, erase, unlock or relock anything.'
