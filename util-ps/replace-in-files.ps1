Param(
	[string]$Files,
	[string]$OldString,
	[string]$NewString
)

$FileItems = Get-Item $Files
$FileItems | ForEach {
	Write-Host "Replacing $OldString with $NewString in $_" -fore Green
	$Content = Get-Content $_.FullName
	$Content = $Content -creplace $OldString, $NewString
	$Content | Set-Content -Path $_.FullName
}
