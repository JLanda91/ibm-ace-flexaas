Param(
	[string]$Ingress,
	[string]$NS
)

$Color = "Yellow"

Write-Host "Exposed ports of ingress ${Ingress} in namespace ${NS}:" -fore $Color

$Result = $(kubectl get ingress.networking.k8s.io -n "${NS}" "${Ingress}" -o jsonpath="{.spec.rules[*].host}") -split "\s+"
$Result | ForEach {
	Write-Host "$_" -fore $Color
}

Return $Result