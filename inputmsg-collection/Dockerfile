FROM jasperlanda/eod20-pyace
RUN pip install requests flask_httpauth
WORKDIR /app
COPY app.py .
CMD ["python3", "./app.py"]