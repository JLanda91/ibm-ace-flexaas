Param(
	[string]$File,
	[string]$NS
)

Write-Host "Creating resources in $File ..."
kubectl create -f $File -n $NS
Write-Host ""