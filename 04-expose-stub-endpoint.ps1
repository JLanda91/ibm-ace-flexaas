$ErrorActionPreference = "Stop"
$NS = "eod20"

Write-Host "Creating stub single pod deployment" -fore Green
.\util-ps\create-k8s-resource.ps1 -File ".\kube-yaml\stub-endpoint-deploy.yaml" -NS "$NS"
.\util-ps\create-k8s-resource.ps1 -File ".\kube-yaml\stub-endpoint-svc.yaml" -NS "$NS"
$StubHost = $(.\util-ps\create-loadbalancer-hostname.ps1 -Service "stub-endpoint-svc" -NS "$NS")
Write-Host "Stub endpoint available at ${StubHost}:8080" -fore Green
