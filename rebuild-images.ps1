Write-Host "Logging into IBM Cloud Container Registry..." -fore Green
ibmcloud cr region-set eu-central
ibmcloud cr login

Foreach($img in $args){
	If (Test-Path ".\image-source\${img}\Dockerfile"){
		Write-Host "Building image eod20-$img" -fore Green
		docker build -t "de.icr.io/landa/eod20-$img" --no-cache ".\image-source\$img"
		docker push "de.icr.io/landa/eod20-$img"
	} Else {
		Write-Host ".\image-source\$img folder does not contain a Dockerfile" -fore Yellow
	}
}