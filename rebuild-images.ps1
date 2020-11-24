Write-Host "Logging into IBM Cloud Container Registry..." -fore Green
ibmcloud cr region-set eu-central
ibmcloud cr login

Foreach($subdir in $args){
	If (Test-Path "${subdir}Dockerfile"){
		$img = [regex]::Match($subdir, '^\.\\([^\\]+)\\$').captures.Groups[1].value
		Write-Host "Building image eod20-$img" -fore Green
		docker build -t "de.icr.io/landa/eod20-$img" --no-cache "$img"
		docker push "de.icr.io/landa/eod20-$img"
	} Else {
		Write-Host "$subdir does not contain a Dockerfile" -fore Yellow
	}
}