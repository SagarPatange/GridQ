# Dockerfile for the messaging file

FROM python:3.11.9

ADD test.py .

RUN pip install sequence 

CMD ["python", "./test.py"]

# FROM python:3.11.9

# ADD message_app.py .

# RUN pip install sequence enum math json onetimpad numpy

# CMD ["python", "./message_app.py"]
