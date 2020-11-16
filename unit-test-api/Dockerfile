FROM jasperlanda/eod20-pyace
RUN pip install flask flask_restful flask_httpauth requests
WORKDIR /unit-test
COPY app.py .
CMD ["python3", "./app.py"]