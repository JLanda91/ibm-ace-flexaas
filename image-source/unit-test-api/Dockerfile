FROM de.icr.io/landa/eod20-pyace
RUN apk add g++ libxml2 libxml2-dev libxslt-dev python3-dev
RUN pip install flask flask_restful flask_httpauth requests lxml
WORKDIR /unit-test
COPY app.py .
CMD ["python3", "./app.py"]