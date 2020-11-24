Param(
	[string]$NS,
	[string]$SecretName,
	[string]$EnvFile
)

$Color = "Yellow"

Write-Host "Creating ACE config secret $SecretName in namespace $NS from env file $EnvFile" -fore $Color
kubectl create secret generic -n $NS $SecretName --from-env-file=$EnvFile
Write-Host ""
