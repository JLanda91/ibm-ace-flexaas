$ErrorActionPreference = "Stop"
$NS = "ace"

Write-Host "Creating namespace $NS" -fore Green
kubectl create ns $NS

Write-Host "Creating ACE single pod deployment" -fore Green
.\util-ps\create-k8s-resource.ps1 -File ".\ace\kube-yaml\ace-deploy.yaml" -NS "$NS"
.\util-ps\create-k8s-resource.ps1 -File ".\ace\kube-yaml\ace-svc.yaml" -NS "$NS"
$AceHost = $(.\util-ps\create-loadbalancer-hostname.ps1 -Service "ace-svc" -NS "$NS")
Write-Host "ACE REST admin available at ${AceHost}:7600" -fore Green

Set-Location "ace/example-bar"
python .\deploy_example_bar.py "${AceHost}:7600"
Set-Location "../.."

