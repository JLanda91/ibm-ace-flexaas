Param(
	[string]$Files,
	[string]$OldString,
	[string]$NewString
)

$Color = "Yellow"

Get-Item $Files| ForEach {
	Write-Host "Replacing $OldString with $NewString in $_" -fore $Color
	$Content = Get-Content $_.FullName
	$Content = $Content -creplace $OldString, $NewString
	$Content | Set-Content -Path $_.FullName
}
