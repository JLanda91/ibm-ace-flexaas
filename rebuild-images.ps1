docker login

foreach($img in $args)
{
	Write-Host "Building image eod20-$img" -fore Green
	docker build -t "jasperlanda/eod20-$img" --no-cache "$img"
	docker push "jasperlanda/eod20-$img"
}