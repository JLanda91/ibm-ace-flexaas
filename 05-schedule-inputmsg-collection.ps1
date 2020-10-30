$ErrorActionPreference = "Stop"
$NS = "eod20"
$Color = "Green"

Write-Host "Creating configmap yaml for ace host params for input message collection" -fore $Color
kubectl create cm -n $NS inputmsg-collection-cm --from-env-file=.\inputmsg-collection\ace-host.env --dry-run=client -o yaml | Set-Content -Path .\kube-yaml\inputmsg-collection-cm.yaml

Write-Host "Creating inputmsg-collection configmap" -fore $Color
.\util-ps\create-k8s-resource.ps1 -File ".\kube-yaml\inputmsg-collection-cm.yaml" -NS "$NS"

Write-Host "Starting input message collection cronjob" -fore $Color
.\util-ps\create-k8s-resource.ps1 -File ".\kube-yaml\inputmsg-collection-cj.yaml" -NS "$NS"