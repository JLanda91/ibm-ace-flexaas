FROM python:3.9-alpine
COPY . /pyace/
WORKDIR /pyace/
RUN python3 setup.py sdist bdist_wheel
RUN pip install ./dist/pyace-0.0.1.tar.gz