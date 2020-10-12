Param(
	[string]$ClusterName = "eod20",
	[string]$ClusterUUID,
	[string]$ClusterRegion = "eu-de",
	[string]$ResourceGroup = "apicpoc"
)

Function ExitWithMessageIf($Condition, $Message){
    If($Condition){
        Write-Host $Message -fore Red
        Write-Host "Exiting..."
        Exit 1
    }
}

#Check if script is being ran as admin, exit otherwise
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
ExitWithMessageIf -Condition $(-Not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) -Message "Must be run as admin"

#Install CLI tools and plugins
$Location = $(Get-Location)
Write-Host "Installing CLI tools and plugins..." -fore Green
Set-ExecutionPolicy Unrestricted
iex(New-Object Net.WebClient).DownloadString('http://ibm.biz/idt-win-installer')
Set-Location $Location

Write-Host "Logging into IBM Cloud..." -fore Green
ibmcloud login -a cloud.ibm.com -r $ClusterRegion -g $ResourceGroup

Write-Host "Setting the Kubernetes context to the IKS instance..." -fore Green
ibmcloud ks cluster config --cluster $ClusterUUID

Write-Host "Getting the current Kubernetes context..." -fore Green
kubectl config current-context

Write-Host "Adding Helm repos" -fore Green
helm repo add iks-charts https://icr.io/helm/iks-charts
#helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

Write-Host "Installing IBM Block Storage Helm chart..." -fore Green
helm install ibm-block-storage iks-charts/ibmcloud-block-storage-plugin -n kube-system

Write-Host "Verify if ibm-block/file storageclasses are created..." -fore Green
kubectl get storageclass

#Write-Host "Installing nginx ingress Helm chart..." -fore Green
#check even welke van de twee werkt
#helm install ingress stable/nginx-ingress --values .\ingress-config.yaml --namespace kube-system
#helm install ingress ingress-nginx/ingress-nginx --values .\ingress-config.yaml -n kube-system

#Write-Host "Waiting for LoadBalancer IP to become available..." -fore Green
#$IngressIP = GetLoadBalancerIP -Service ingress-ingress-nginx-controller -NS kube-system

#Write-Host "LoadBalancer IP found: $IngressIP" -fore Green
#Write-Host "Creating NLB DNS at this IP..." -fore Green
#$IngressHost = CreateHostName -ip $IngressIP

#Write-Host "Hostname created for ingress-nginx: $NLBHost" -fore Green
# Write-Host "Installing Certman..." -fore Green
# kubectl create -f https://github.com/jetstack/cert-manager/releases/download/v0.12.0/cert-manager.yaml

Write-Host "Creating secret from dockerconfig json..." -fore Green
kubectl create secret generic regcred --from-file=.dockerconfigjson=$HOME\.docker\config.json --type=kubernetes.io/dockerconfigjson
