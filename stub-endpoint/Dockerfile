FROM jasperlanda/eod20-pyace
RUN pip install requests flask flask_httpauth
WORKDIR /stub
COPY app.py .
CMD ["python3", "./app.py"]