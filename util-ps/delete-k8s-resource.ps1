Param(
	[string]$File,
	[string]$NS
)

Write-Host "Deleting resources in $File ..."
kubectl delete -f $File -n $NS
Write-Host ""