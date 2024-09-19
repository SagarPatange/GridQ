# Dockerfile for the messaging file

FROM python:3.9

ADD message_app.py .

RUN pip install sequence 

CMD ["python", "./message_app.py"]