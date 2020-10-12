Write-Host "Creating namespace ace" -fore Green
kubectl create ns ace

Write-Host "Creating ACE single pod deployment" -fore Green
.\util-ps\create-k8s-resource.ps1 -File ".\ace\kube-yaml\ace-deploy.yaml" -NS "ace"
.\util-ps\create-k8s-resource.ps1 -File ".\ace\kube-yaml\ace-svc.yaml" -NS "ace"
$AceHost = $(.\util-ps\create-loadbalancer-hostname.ps1 -Service "ace-svc" -NS "ace")
Write-Host "ACE REST admin available at ${AceHost}:7600" -fore Green

Set-Location "ace/example-bar"
python .\deploy_example_bar.py "${AceHost}:7600"
Set-Location "../.."

.\util-ps\replace-in-files.ps1 -Files ".\inputmsg-collection\ace-host.env" -OldString "host=.+" -NewString "host=${AceHost}"

