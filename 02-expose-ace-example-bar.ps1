$ErrorActionPreference = "Stop"
$NS = "ace"
$Color = "Green"
$AcePort = 7600

Write-Host "Creating namespace $NS" -fore $Color
kubectl create ns $NS

foreach ($ta in "test","accp"){
	Write-Host "Creating ACE (${ta}) single pod deployment" -fore $Color
	.\util-ps\create-k8s-resource.ps1 -File ".\kube-yaml\ace-${ta}-deploy.yaml" -NS "$NS"
	.\util-ps\create-k8s-resource.ps1 -File ".\kube-yaml\ace-${ta}-svc.yaml" -NS "$NS"
	.\util-ps\create-k8s-resource.ps1 -File ".\kube-yaml\ace-${ta}-ingress.yaml" -NS "$NS"
	$Hosts = .\util-ps\get-ingress-hosts.ps1 -Ingress "ace-${ta}-ingress" -NS "$NS" 
	$Admin = $Hosts[0]
	
	Set-Location "ace/example-bar"
	python .\deploy_example_bar.py "$Admin"
	Set-Location "../.."
}


