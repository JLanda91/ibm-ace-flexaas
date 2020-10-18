Param(
	[string]$NS
)

$Color = "Yellow"

Write-Host "Deleting all Kubernetes resources in namespace $NS" -fore $Color
kubectl delete ns $NS
Write-Host ""