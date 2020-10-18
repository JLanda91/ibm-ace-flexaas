Param(
	[string]$File,
	[string]$NS
)

$Color = "Yellow"

Write-Host "Deleting resources in $File ..." - fore $Color
kubectl delete -f $File -n $NS
Write-Host ""