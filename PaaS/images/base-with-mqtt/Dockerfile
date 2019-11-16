FROM python:3-slim
RUN apt-get update
RUN apt-get -y install iputils-ping
RUN apt-get -y install systemd
RUN apt-get -y install mosquitto
RUN pip3 install paho-mqtt
RUN pip3 install pika
ADD hello.py /
CMD ["python", "./hello.py"]
