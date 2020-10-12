# login bij Docker
docker login

foreach($img in "ace","inputmsg-collection")
{
	Write-Host "Building image eod20-$img" -fore Green
	docker build -t "jasperlanda/eod20-$img" "$img"
	docker push "jasperlanda/eod20-$img"
}