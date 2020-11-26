$ErrorActionPreference = "Stop"
$NS = "ace"
$Color = "Green"

.\util-ps\create-k8s-ns-and-ips.ps1 -NS $NS

foreach ($ta in "test","accp"){
	Write-Host "Creating ACE (${ta}) single pod deployment" -fore $Color
	.\util-ps\apply-k8s-resource.ps1 -File ".\ace-kube-yaml\ace-${ta}-deploy.yaml" -NS "$NS"
	.\util-ps\apply-k8s-resource.ps1 -File ".\ace-kube-yaml\ace-${ta}-svc.yaml" -NS "$NS"
	.\util-ps\apply-k8s-resource.ps1 -File ".\ace-kube-yaml\ace-${ta}-ingress.yaml" -NS "$NS"
	.\util-ps\get-ingress-hosts.ps1 -Ingress "ace-${ta}-ingress" -NS "$NS"  | Out-Null
}


