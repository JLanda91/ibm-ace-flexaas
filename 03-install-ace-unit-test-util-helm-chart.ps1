$ErrorActionPreference = "Stop"
$NS = "eod20"
$Color = "Green"

.\util-ps\create-k8s-ns-and-ips.ps1 -NS $NS

Write-Host "Installing ace-unit-test-util Helm Chart in namespace $NS ... " -fore $Color
helm install ace-unit-test-util .\helm\ace-unit-test-util\ -n $NS
