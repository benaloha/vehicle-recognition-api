# Copyright © 2019 by Spectrico
# Licensed under the MIT License
# Based on the tutorial by Adrian Rosebrock: https://www.pyimagesearch.com/2018/11/12/yolo-object-detection-with-opencv/
# Usage: $ python car_color_classifier_yolo3.py --image cars.jpg

import argparse
import os
import time
import cv2
import numpy as np
import color_classifier
import model_classifier

class CarClassifier():
	def __init__(self, confidence_treshold, non_max_supr_treshold):

		start = time.time()
		
		self.yolo_map = "yolo-coco"
		self.confidence_treshold = confidence_treshold
		self.non_max_supr_treshold = non_max_supr_treshold

		# construct the argument parse and parse the arguments
		self.color_classifier = color_classifier.Classifier()
		self.model_classifier = model_classifier.Classifier()

		# load the COCO class labels our YOLO model was trained on
		labelsPath = os.path.sep.join([self.yolo_map, "coco.names"])
		self.LABELS = open(labelsPath).read().strip().split("\n")

		# initialize a list of colors to represent each possible class label
		np.random.seed(42)
		self.COLORS = np.random.randint(0, 195, size=(len(self.LABELS), 3), dtype="uint8")

		# derive the paths to the YOLO weights and model configuration
		weightsPath = os.path.sep.join([self.yolo_map, "yolov3.weights"])
		configPath = os.path.sep.join([self.yolo_map, "yolov3.cfg"])

		# load our YOLO object detector trained on COCO dataset (80 classes)
		print("[INFO] loading YOLO from disk...")
		self.net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)

		end = time.time()
		print("[INFO] CarClassifier.init() took {:.6f} seconds".format(end - start))


	def predict(self, image):

		start = time.time()

		# grab its spatial dimensions
		(H, W) = image.shape[:2]

		# determine only the *output* layer names that we need from YOLO
		layer_names = self.net.getLayerNames()
		output_layers = [layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

		# construct a blob from the input image and then perform a forward
		# pass of the YOLO object detector, giving us our bounding boxes and
		# associated probabilities
		blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
		self.net.setInput(blob)
		outputs = self.net.forward(output_layers)
		end = time.time()

		# show timing information on YOLO
		print("[INFO] object detection took {:.6f} seconds".format(end - start))

		# initialize our lists of detected bounding boxes, confidences, and
		# class IDs, respectively
		boxes = []
		confidences = []
		classIDs = []

		# loop over each of the layer outputs
		for output in outputs:
			# loop over each of the detections
			for detection in output:
				# extract the class ID and confidence (i.e., probability) of
				# the current object detection
				scores = detection[5:]
				classID = np.argmax(scores)
				confidence = scores[classID]

				# filter out weak predictions by ensuring the detected
				# probability is greater than the minimum probability
				if confidence > self.confidence_treshold:
					# scale the bounding box coordinates back relative to the
					# size of the image, keeping in mind that YOLO actually
					# returns the center (x, y)-coordinates of the bounding
					# box followed by the boxes' width and height
					box = detection[0:4] * np.array([W, H, W, H])
					(centerX, centerY, width, height) = box.astype("int")

					# use the center (x, y)-coordinates to derive the top and
					# and left corner of the bounding box
					x = int(centerX - (width / 2))
					y = int(centerY - (height / 2))

					# update our list of bounding box coordinates, confidences,
					# and class IDs
					boxes.append([x, y, int(width), int(height)])
					confidences.append(float(confidence))
					classIDs.append(classID)

		# apply non-maxima suppression to suppress weak, overlapping bounding
		# boxes
		idxs = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence_treshold, self.non_max_supr_treshold)

		objects = []
		# ensure at least one detection exists
		if len(idxs) > 0:
			# loop over the indexes we are keeping
			for i in idxs.flatten():
				# extract the bounding box coordinates
				(x, y) = (boxes[i][0], boxes[i][1])
				(w, h) = (boxes[i][2], boxes[i][3])
				# draw a bounding box rectangle and label on the image
				color = [int(c) for c in self.COLORS[classIDs[i]]]
				if classIDs[i] == 2:
					color_result = self.color_classifier.predict(image[max(y, 0):y + h, max(x, 0):x + w])
					model_result = self.model_classifier.predict(image[max(y, 0):y + h, max(x, 0):x + w])

					color_car = color_result[0]['color']
					color_prob = float(color_result[0]['prob'])
					color_txt = "{}: {}".format(color_car, color_prob)					
					cv2.putText(image, color_txt, (x + 2, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

					make_car = model_result[0]['make']
					make_prob = float(model_result[0]['prob'])
					make_txt = "{}: {}".format(make_car, make_prob)										
					cv2.putText(image, make_txt, (x + 2, y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

					model_car = model_result[0]['model']
					cv2.putText(image, model_car, (x + 2, y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

					car = {"make": make_car, "make_prob": make_prob, "model": model_car, "color": color_car, "color_prob": color_prob}
					print("[Response] {}".format(car))
					objects.append(car)

				cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)

		# output image
		#cv2.imwrite("data/output.jpg", image)

		# show timing information on MobileNet classifier
		end = time.time()
		print("[INFO] CarClassifier.predict() took {:.6f} seconds".format(end - start))
		return objects
