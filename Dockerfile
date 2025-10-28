# Dockerfile for the messaging file

FROM python:3.11.9

ADD main.py .

WORKDIR /GRIDQ

COPY . /GRIDQ

RUN pip install --no-cache-dir -r docker_requirements.txt

CMD ["python", "main.py"]
