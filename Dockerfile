FROM python:3.8-slim-buster

ENV IMG img.jpg

RUN apt-get update
RUN apt-get install -y wget ffmpeg libsm6 libxext6

RUN pip install --upgrade pip
RUN pip install tensorflow
RUN pip install opencv-python
RUN pip install Pillow
RUN pip install six

# download models al op fs host gedownload, dan hoeft het niet steeds in docker
# stap te gebeuren, is behoorlijk traag.
#WORKDIR /opt/car/yolo-coco
#RUN wget https://pjreddie.com/media/files/yolov3.weights

COPY . /opt/car
WORKDIR /opt/car

CMD python car_recognition_server.py
