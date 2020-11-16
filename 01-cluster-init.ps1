Param(
	[string]$ClusterName = "eod20",
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
ibmcloud ks cluster config --cluster $ClusterName

Write-Host "Getting the current Kubernetes context..." -fore $Color
kubectl config current-context

Write-Host "Creating secret from dockerconfig json..." -fore $Color
kubectl create secret generic regcred --from-file=.dockerconfigjson=$HOME\.docker\config.json --type=kubernetes.io/dockerconfigjson

Write-Host "Getting cluster ALB hostname and replace in ingress rules..." -fore $Color
$ClusterHostName = .\util-ps\get-cluster-hostname -ClusterName "$ClusterName"

If ($ClusterHostName -ne ""){
	.\util-ps\replace-in-files -Files ".\kube-yaml\*-ingress.yaml" -OldString "$\S+-\d{4}" -NewString "$ClusterHostName"
}