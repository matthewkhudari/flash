FROM python:3.7-alpine
WORKDIR /flash
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASH_SECRET_KEY=dev
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
