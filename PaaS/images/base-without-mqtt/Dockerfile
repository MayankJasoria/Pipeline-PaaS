FROM python:3-slim
RUN apt-get update
RUN apt-get -y install iputils-ping
RUN pip3 install pika
ADD hello.py /
CMD ["python", "./hello.py"]
