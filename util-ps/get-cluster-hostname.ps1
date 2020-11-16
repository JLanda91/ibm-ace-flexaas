Param(
	[string]$ClusterName
)

Try {
	Return [regex]::Match($(ibmcloud ks ingress secret ls -c $ClusterName --output json), '"name": "(\S+)"').captures.Groups[1].value
} Catch [RuntimeException] {
	Write-Host "Cluster host name could not be determined" -fore "Red"
	Return ""
}