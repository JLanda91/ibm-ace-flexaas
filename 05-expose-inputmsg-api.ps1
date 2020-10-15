$ErrorActionPreference = "Stop"
$NS = "eod20"

Write-Host "Creating secret yamls for input message API users" -fore Green
kubectl create secret generic -n $NS inputmsg-api-user1-secret --from-env-file=.\inputmsg-api\user1.env --dry-run=client -o yaml | Set-Content -Path .\kube-yaml\inputmsg-api-user1-secret.yaml
kubectl create secret generic -n $NS inputmsg-api-user2-secret --from-env-file=.\inputmsg-api\user2.env --dry-run=client -o yaml | Set-Content -Path .\kube-yaml\inputmsg-api-user2-secret.yaml

Write-Host "Creating input message API user secrets" -fore Green
.\util-ps\create-k8s-resource.ps1 -File ".\kube-yaml\inputmsg-api-user1-secret.yaml" -NS "$NS"
.\util-ps\create-k8s-resource.ps1 -File ".\kube-yaml\inputmsg-api-user2-secret.yaml" -NS "$NS"

Write-Host "Starting input message API deployment" -fore Green
.\util-ps\create-k8s-resource.ps1 -File ".\kube-yaml\inputmsg-api-deploy.yaml" -NS "$NS"
.\util-ps\create-k8s-resource.ps1 -File ".\kube-yaml\inputmsg-api-svc.yaml" -NS "$NS"
