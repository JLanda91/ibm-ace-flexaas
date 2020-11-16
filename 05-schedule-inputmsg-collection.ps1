$ErrorActionPreference = "Stop"
$NS = "eod20"
$Color = "Green"

Write-Host "Creating secret for ace host params for input message collection" -fore $Color
.\util-ps\create-ace-config.ps1 -NS "$NS" -SecretName "ace-config"

Write-Host "Starting input message collection cronjob" -fore $Color
.\util-ps\apply-k8s-resource.ps1 -File ".\kube-yaml\inputmsg-collection-cj.yaml" -NS "$NS"