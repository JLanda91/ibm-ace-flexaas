$ErrorActionPreference = "Stop"
$NS = "eod20"
$Color = "Green"
$ApiPort = 8080

Write-Host "Adding Helm repo for IBM Cloud block and file storageclasses" -fore $Color
helm repo add iks-charts https://icr.io/helm/iks-charts
helm repo update

Write-Host "Installing IBM Block/File Storage Helm chart..." -fore $Color
helm install ibm-block-storage iks-charts/ibmcloud-block-storage-plugin -n kube-system

Write-Host "Verify if IBM Block/File storageclasses are created..." -fore $Color
kubectl get storageclass

Write-Host "Creating secret yamls for input message API users" -fore $Color
kubectl create secret generic -n $NS inputmsg-api-users-secret --from-env-file=.\inputmsg-api\users.env --dry-run=client -o yaml | Set-Content -Path .\kube-yaml\inputmsg-api-users-secret.yaml

Write-Host "Starting input message API deployment" -fore $Color
.\util-ps\create-k8s-resource.ps1 -File ".\kube-yaml\inputmsg-api-users-secret.yaml" -NS "$NS"
.\util-ps\create-k8s-resource.ps1 -File ".\kube-yaml\inputmsg-api-pvc.yaml" -NS "$NS"
.\util-ps\create-k8s-resource.ps1 -File ".\kube-yaml\inputmsg-api-deploy.yaml" -NS "$NS"
.\util-ps\create-k8s-resource.ps1 -File ".\kube-yaml\inputmsg-api-svc.yaml" -NS "$NS"
.\util-ps\create-k8s-resource.ps1 -File ".\kube-yaml\inputmsg-api-ingress.yaml" -NS "$NS"
.\util-ps\get-ingress-hosts.ps1 -Ingress "inputmsg-api-ingress" -NS "$NS" | Out-Null
