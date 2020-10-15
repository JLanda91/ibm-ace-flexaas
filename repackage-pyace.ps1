Set-Location ".\pyace\"

foreach($folder in "build","dist","pyace.egg-info"){
	Remove-Item -path $folder -recurse
}

python setup.py sdist bdist_wheel
pip install ./dist/pyace-0.0.1.tar.gz
Set-Location ".."