$ErrorActionPreference = "Stop"
$NS = "eod20"
$Color = "Green"
$StubPort = 8080

Write-Host "Creating namespace $NS" -fore $Color
kubectl create ns $NS

Write-Host "Creating stub single pod deployment" -fore $Color
.\util-ps\apply-k8s-resource.ps1 -File ".\kube-yaml\stub-endpoint-deploy.yaml" -NS "$NS"
.\util-ps\apply-k8s-resource.ps1 -File ".\kube-yaml\stub-endpoint-svc.yaml" -NS "$NS"
.\util-ps\apply-k8s-resource.ps1 -File ".\kube-yaml\stub-endpoint-ingress.yaml" -NS "$NS"
.\util-ps\get-ingress-hosts.ps1 -Ingress "stub-endpoint-ingress" -NS "$NS" | Out-Null
