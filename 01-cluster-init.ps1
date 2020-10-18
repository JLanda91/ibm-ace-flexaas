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

$Color = "Green"

#Check if script is being ran as admin, exit otherwise
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
ExitWithMessageIf -Condition $(-Not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) -Message "Must be run as admin"

#Install CLI tools and plugins
$Location = $(Get-Location)
Write-Host "Installing CLI tools and plugins..." -fore $Color
Set-ExecutionPolicy Unrestricted
iex(New-Object Net.WebClient).DownloadString('http://ibm.biz/idt-win-installer')
Set-Location $Location

Write-Host "Logging into IBM Cloud..." -fore $Color
ibmcloud login -a cloud.ibm.com -r $ClusterRegion -g $ResourceGroup

Write-Host "Setting the Kubernetes context to the IKS instance..." -fore $Color
ibmcloud ks cluster config --cluster $ClusterUUID

Write-Host "Getting the current Kubernetes context..." -fore $Color
kubectl config current-context

#Write-Host "Installing nginx ingress Helm chart..." -fore $Color
#check even welke van de twee werkt
#helm install ingress stable/nginx-ingress --values .\ingress-config.yaml --namespace kube-system
#helm install ingress ingress-nginx/ingress-nginx --values .\ingress-config.yaml -n kube-system

#Write-Host "Waiting for LoadBalancer IP to become available..." -fore $Color
#$IngressIP = GetLoadBalancerIP -Service ingress-ingress-nginx-controller -NS kube-system

#Write-Host "LoadBalancer IP found: $IngressIP" -fore $Color
#Write-Host "Creating NLB DNS at this IP..." -fore $Color
#$IngressHost = CreateHostName -ip $IngressIP

#Write-Host "Hostname created for ingress-nginx: $NLBHost" -fore $Color
# Write-Host "Installing Certman..." -fore $Color
# kubectl create -f https://github.com/jetstack/cert-manager/releases/download/v0.12.0/cert-manager.yaml

Write-Host "Creating secret from dockerconfig json..." -fore $Color
kubectl create secret generic regcred --from-file=.dockerconfigjson=$HOME\.docker\config.json --type=kubernetes.io/dockerconfigjson
