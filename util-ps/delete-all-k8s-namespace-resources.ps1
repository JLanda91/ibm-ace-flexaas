Param(
	[string]$NS
)

Write-Host "Deleting all Kubernetes resources in namespace $NS"
kubectl delete ns $NS
Write-Host ""