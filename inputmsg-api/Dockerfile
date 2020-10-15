FROM jasperlanda/eod20-pyace
RUN pip install flask flask_httpauth
WORKDIR /inputmsg-api
COPY app.py .
CMD ["python3", "./app.py"]