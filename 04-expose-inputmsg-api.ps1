$ErrorActionPreference = "Stop"
$NS = "eod20"
$Color = "Green"

Write-Host "Adding Helm repo for IBM Cloud block and file storageclasses" -fore $Color
helm repo add iks-charts https://icr.io/helm/iks-charts
helm repo update

Write-Host "Installing IBM Block/File Storage Helm chart..." -fore $Color
helm install ibm-block-storage iks-charts/ibmcloud-block-storage-plugin -n kube-system

Write-Host "Verify if IBM Block/File storageclasses are created..." -fore $Color
kubectl get storageclass

Write-Host "Creating secret yamls for input message API users" -fore $Color
kubectl create secret generic -n $NS inputmsg-api-user1-secret --from-env-file=.\inputmsg-api\user1.env --dry-run=client -o yaml | Set-Content -Path .\kube-yaml\inputmsg-api-user1-secret.yaml
kubectl create secret generic -n $NS inputmsg-api-user2-secret --from-env-file=.\inputmsg-api\user2.env --dry-run=client -o yaml | Set-Content -Path .\kube-yaml\inputmsg-api-user2-secret.yaml

Write-Host "Starting input message API deployment" -fore $Color
.\util-ps\create-k8s-resource.ps1 -File ".\kube-yaml\inputmsg-api-user1-secret.yaml" -NS "$NS"
.\util-ps\create-k8s-resource.ps1 -File ".\kube-yaml\inputmsg-api-user2-secret.yaml" -NS "$NS"
.\util-ps\create-k8s-resource.ps1 -File ".\kube-yaml\inputmsg-api-pvc.yaml" -NS "$NS"
.\util-ps\create-k8s-resource.ps1 -File ".\kube-yaml\inputmsg-api-deploy.yaml" -NS "$NS"
.\util-ps\create-k8s-resource.ps1 -File ".\kube-yaml\inputmsg-api-svc.yaml" -NS "$NS"

$ApiHost = $(.\util-ps\create-loadbalancer-hostname.ps1 -Service "inputmsg-api-svc" -NS "$NS")
Write-Host "Input message API available at ${ApiHost}:8080" -fore $Color
