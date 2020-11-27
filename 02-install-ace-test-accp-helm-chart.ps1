$ErrorActionPreference = "Stop"
$NS = "ace"
$Color = "Green"

.\util-ps\create-k8s-ns-and-ips.ps1 -NS $NS

Write-Host "Installing ace-test-accp Helm Chart in namespace $NS ... " -fore $Color
helm install ace-test-accp .\helm\ace-test-accp\ -n $NS