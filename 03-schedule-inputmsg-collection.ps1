$ErrorActionPreference = "Stop"
$NS = "eod20"

Write-Host "Creating namespace $NS" -fore Green
kubectl create ns $NS

Write-Host "Creating secret yaml for ace host params for input message collection" -fore Green
kubectl create secret generic -n $NS inputmsg-collection-secret --from-env-file=.\inputmsg-collection\ace-host.env --dry-run=client -o yaml | Set-Content -Path .\inputmsg-collection\kube-yaml\inputmsg-collection-secret.yaml

Write-Host "Creating inputmsg-collection-config secret" -fore Green
.\util-ps\create-k8s-resource.ps1 -File ".\inputmsg-collection\kube-yaml\inputmsg-collection-secret.yaml" -NS "$NS"

Write-Host "Starting input message collection cronjob" -fore Green
.\util-ps\create-k8s-resource.ps1 -File ".\inputmsg-collection\kube-yaml\inputmsg-collection-cj.yaml" -NS "$NS"