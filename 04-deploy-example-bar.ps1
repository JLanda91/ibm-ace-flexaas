$ErrorActionPreference = "Stop"
$NS = "ace"
$Color = "Green"

Write-Host "Deploying example BAR to ACE test and accp.. " -fore $Color

foreach ($ta in "test","accp"){
	$Hosts = .\util-ps\get-ingress-hosts.ps1 -Ingress "ace-${ta}-ingress" -NS "$NS" 
	$Admin = $Hosts[0]
	
	Set-Location "example-bar"
	python .\deploy_example_bar.py "$Admin"
	Set-Location ".."
}


