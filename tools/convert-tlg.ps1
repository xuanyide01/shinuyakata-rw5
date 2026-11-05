param([string]$Plan)
$ErrorActionPreference='Stop'
[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$lib=[IO.Path]::GetFullPath((Join-Path $root '../研究/GARbro'))
Add-Type -AssemblyName PresentationCore,WindowsBase
[Reflection.Assembly]::LoadFrom((Join-Path $lib 'GameRes.dll'))|Out-Null
[Reflection.Assembly]::LoadFrom((Join-Path $lib 'ArcFormats.dll'))|Out-Null
$format=New-Object GameRes.Formats.KiriKiri.TlgFormat
$items=Get-Content -LiteralPath $Plan -Raw -Encoding UTF8|ConvertFrom-Json
$done=0
foreach($p in $items){
 [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($p.output))|Out-Null
 if(!(Test-Path -LiteralPath $p.output)){
  $stream=[GameRes.BinaryStream]::FromFile($p.input)
  try{
   $meta=$format.ReadMetaData($stream);if(!$meta){throw 'Invalid TLG metadata'}
   $stream.Position=0;$decoded=$format.Read($stream,$meta)
   $encoder=New-Object System.Windows.Media.Imaging.PngBitmapEncoder
   $encoder.Frames.Add([System.Windows.Media.Imaging.BitmapFrame]::Create($decoded.Bitmap))
   $output=[IO.File]::Create($p.output)
   try{$encoder.Save($output)}finally{$output.Dispose()}
  }finally{$stream.Dispose()}
 }
 $done++;if($done%100-eq 0){[Console]::WriteLine('TLG_TO_PNG '+$done)}
 if($done%40-eq 0){[GC]::Collect()}
}
[Console]::WriteLine('TLG_COMPLETE '+$done)
