FROM python:3.8-slim-buster

RUN apt-get update

RUN apt-get install -y wget ffmpeg libsm6 libxext6

RUN pip install numpy

RUN pip install opencv-python

RUN pip install MNN

RUN pip install six

RUN mkdir -p /opt/car/yolov4

WORKDIR /opt/car/yolov4

#Download models
RUN wget https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights

COPY . /opt/car

WORKDIR /opt/car

CMD python car_recognition_server.py