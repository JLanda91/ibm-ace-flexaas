Param(
	[string]$NS
)

$Color = "Yellow"

Write-Host "Creating namespace $NS" -fore $Color
kubectl create ns $NS
kubectl create secret -n $NS docker-registry icr --docker-server=de.icr.io --docker-username=iamapikey --docker-password=$env:ICRApiKey
Write-Host ""
