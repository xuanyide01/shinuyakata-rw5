param([string]$Mode='interface')
$ErrorActionPreference='Stop'
[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$research=[IO.Path]::GetFullPath((Join-Path $root '../研究'))
$lib=Join-Path $research 'GARbro'
[Reflection.Assembly]::LoadFrom((Join-Path $lib 'GameRes.dll')) | Out-Null
[Reflection.Assembly]::LoadFrom((Join-Path $lib 'ArcFormats.dll')) | Out-Null
$stream=[IO.File]::OpenRead((Join-Path $lib 'GameData/Formats.dat'))
try { [GameRes.FormatCatalog]::Instance.DeserializeScheme($stream) } finally { $stream.Dispose() }
Add-Type -Path (Join-Path $PSScriptRoot 'decode-resources.cs') -ReferencedAssemblies @((Join-Path $lib 'GameRes.dll'),(Join-Path $lib 'ArcFormats.dll'),'System.Core','System.Web.Extensions','System.IO.Compression')
$output=Join-Path $research 'decoded-resources'
if($Mode -eq 'restore-original-files') {
    $output=[IO.Path]::GetFullPath((Join-Path $root '../原始资源解码'))
    $expected=[IO.Path]::GetFullPath((Join-Path $root '../原始资源解码'))
    if($output -ne $expected){throw 'Unexpected restoration output'}
}
[DecodeYakataResources]::Run('I:/galgame/游戏本体/死馆/死に逝く君、館に芽吹く憎悪',(Join-Path $root 'reports/extraction-manifest.json'),(Join-Path $research 'bug02_yakata.tpm.research-copy'),$output,(Join-Path $root ('reports/decode-'+$Mode+'.json')),$Mode)
