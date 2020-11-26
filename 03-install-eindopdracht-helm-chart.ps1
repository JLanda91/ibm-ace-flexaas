$ErrorActionPreference = "Stop"
$NS = "eod20"
$Color = "Green"
$Version = 0.1.0

.\util-ps\create-k8s-ns-and-ips.ps1 -NS $NS

Write-Host "Installing eindopdracht Helm Chart in namespace $NS ... " -fore $Color
helm install ace-unit-test-util .\helm\ace-unit-test-util\ --version $Version -n $NS
