FROM python:3.7-alpine
WORKDIR /flash
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["python", "worker.py"]
