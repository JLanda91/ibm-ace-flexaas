Param(
	[string]$ClusterName
)

Return [regex]::Match($(ibmcloud ks ingress secret ls -c $ClusterName --output json), '"name": "(\S+)"').captures.Groups[1].value
