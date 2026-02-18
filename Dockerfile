FROM python:3.12-slim

COPY requirements.txt .
COPY uploader.py .

RUN pip install -r requirements.txt

CMD ["python", "uploader.py"]