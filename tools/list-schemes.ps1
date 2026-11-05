$ErrorActionPreference='Stop'
[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
$lib=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../研究/GARbro'))
[Reflection.Assembly]::LoadFrom((Join-Path $lib 'GameRes.dll')) | Out-Null
[Reflection.Assembly]::LoadFrom((Join-Path $lib 'ArcFormats.dll')) | Out-Null
$schemeFile=Join-Path $lib 'GameData/Formats.dat'
$stream=[IO.File]::OpenRead($schemeFile)
try { [GameRes.FormatCatalog]::Instance.DeserializeScheme($stream) } finally { $stream.Dispose() }
$flags=[Reflection.BindingFlags]'Instance,Public,NonPublic'
$all=@()
foreach($entry in [GameRes.Formats.KiriKiri.Xp3Opener]::KnownSchemes.GetEnumerator()) {
    $crypt=$entry.Value
    if($crypt -is [GameRes.Formats.KiriKiri.CxEncryption]) {
        $base=[GameRes.Formats.KiriKiri.CxEncryption]
        $mask=$base.GetField('m_mask',$flags).GetValue($crypt)
        $offset=$base.GetField('m_offset',$flags).GetValue($crypt)
        if(($mask -eq 0x17b -and $offset -eq 0x35a) -or $entry.Key -match 'Shini|Yakata|死に|芽吹') {
            $v=@{name=$entry.Key;type=$crypt.GetType().FullName;m_mask=$mask;m_offset=$offset}
            foreach($name in @('PrologOrder','EvenBranchOrder','OddBranchOrder','TpmFileName','ControlBlock')) {
                $v[$name]=$base.GetField($name,$flags).GetValue($crypt)
            }
            $all+=$v
            [Console]::WriteLine(($v | Select-Object @{n='Name';e={$_.name}},@{n='Type';e={$_.type}},@{n='Mask';e={$_.m_mask}},@{n='Offset';e={$_.m_offset}} | ConvertTo-Json -Compress))
        }
    }
}
$dest=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../reports/known-cx-profiles.json'))
[IO.File]::WriteAllText($dest,(ConvertTo-Json -InputObject @($all) -Depth 8),[Text.UTF8Encoding]::new($false))
[Console]::WriteLine('MATCHING_PROFILES '+$all.Count)
