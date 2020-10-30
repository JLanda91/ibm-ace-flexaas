Param(
	[string]$Service,
	[string]$NS,
	[string]$ClusterName = "eod20",
	[string]$Port
)

$ErrorActionPreference = "Stop"
$Color = "Yellow"

$ip = ''
While($ip -eq ''){
	Start-Sleep -s 3
	$ip = $(kubectl -n $NS get service $Service -o jsonpath="{.status.loadBalancer.ingress[0].ip}")
}
Write-Host "Creating hostname for K8s LoadBalancer service $Service in namespace $NS ($ip)..." -fore $Color
$NLBDNSOutput = $(ibmcloud ks nlb-dns create classic --cluster $ClusterName --ip $ip)
Write-Host $NLBDNSOutput[1] -fore $Color
Write-Host ""
$Dummy = $NLBDNSOutput[1] -match "\S+$"
$HostName = $Matches[0]
Write-Host "${Service}.${NS} externally available at ${HostName}:${Port}" -fore $Color
Return $HostName