$ErrorActionPreference = "Stop"
$NS = "eod20"
$Color = "Green"

Write-Host "Creating secret for unit test API users" -fore $Color
kubectl create secret generic -n $NS unit-test-api-users-secret --from-env-file=.\unit-test-api\users.env

Write-Host "Creating secret for ace host params for input message collection" -fore $Color
.\util-ps\create-ace-config.ps1 -NS $NS -SecretName "ace-config"

Write-Host "Starting input message API deployment" -fore $Color
.\util-ps\apply-k8s-resource.ps1 -File ".\kube-yaml\unit-test-api-pvc.yaml" -NS "$NS"
.\util-ps\apply-k8s-resource.ps1 -File ".\kube-yaml\unit-test-api-deploy.yaml" -NS "$NS"
.\util-ps\apply-k8s-resource.ps1 -File ".\kube-yaml\unit-test-api-svc.yaml" -NS "$NS"
.\util-ps\apply-k8s-resource.ps1 -File ".\kube-yaml\unit-test-api-ingress.yaml" -NS "$NS"
.\util-ps\get-ingress-hosts.ps1 -Ingress "unit-test-api-ingress" -NS "$NS" | Out-Null