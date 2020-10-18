Param(
	[string]$File,
	[string]$NS
)

$Color = "Yellow"

Write-Host "Creating resources in $File ..." -fore $Color
kubectl create -f $File -n $NS
Write-Host ""