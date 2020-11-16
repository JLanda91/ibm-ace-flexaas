Set-Location ".\pyace\"

foreach($folder in "build","dist","pyace.egg-info"){
	If (Test-Path $folder){
		Remove-Item -path $folder -recurse
	}
}

# MAKE SURE TO 'pip install wheel' FIRST
python setup.py sdist bdist_wheel
pip install ./dist/pyace-0.0.1.tar.gz
Set-Location ".."