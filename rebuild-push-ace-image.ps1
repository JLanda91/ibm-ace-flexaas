# login bij Docker
docker login

# build image vanuit ace/Dockerfile
docker build -t jasperlanda/eod20-ace ace -f ace/Dockerfile-ace

# push naar dockerhub
docker push jasperlanda/eod20-ace