Param(
	[string]$NS,
	[string]$SecretName
)

$Color = "Yellow"

kubectl create secret generic -n $NS $SecretName --from-env-file=.\ace\ace-host.env
