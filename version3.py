import cv2
import numpy as np
import boto3
from call import send_message
import pygame.mixer
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import time
import sys

pygame.mixer.init()
scale_factor = .30
green = (0,255,0)
red = (0,0,255)
frame_thickness = 2
capture = cv2.VideoCapture(0)
rekognition = boto3.client('rekognition')

#need to combine with lego
#X_MAX = 2370
#X_MIN = 720
#X_HOME = 1545
#Y_MAX = 2300
#Y_MIN = 1000
#Y_HOME = 1650
#now_degree_x, now_degree_y, move_degree_x, move_degree_y = X_HOME, Y_HOME, 0, 0

#setting the MQTTClient for greengrass
myMQTTClient = AWSIoTMQTTClient("raspi")
myMQTTClient.configureEndpoint("Endpoint url", 443)
myMQTTClient.configureCredentials("/xxx/xxx/cert/AmazonRootCA1.pem", "/xxx/xxx/cert/xxx-private.pem.key", "/xxx/xxx/cert/xxx-certificate.pem.crt")
myMQTTClient.configureOfflinePublishQueueing(-1)
myMQTTClient.configureDrainingFrequency(2)
myMQTTClient.configureConnectDisconnectTimeout(10)
myMQTTClient.configureMQTTOperationTimeout(5)
myMQTTClient.connect()
#print ("Connected to AWS IoT")

fontscale = 2.0
color = (0, 0, 0)
fontface = cv2.FONT_HERSHEY_SIMPLEX

while(True):

    ret, frame = capture.read()
    height, width, channels = frame.shape
    image = cv2.resize(frame, (int(width * scale_factor), int(height * scale_factor)))
    ret, buf = cv2.imencode('.jpg', image)
    faces = rekognition.detect_faces(Image={'Bytes':buf.tobytes()}, Attributes=['ALL'])
#   facerect = cascade.detectMultiScale(frame, scaleFactor=1.2, minNeighbors=2, minSize=(10, 10))
#   for rect in facerect:
#       img_x = rect[0]+rect[2]/2
#       img_y = rect[1]+rect[3]/2
#       move_degree_x = now_degree_x - (img_x-160)*0.3
#       move_degree_y = now_degree_y + (img_y-160)*0.3
#
    for face in faces['FaceDetails']:
        sad = face['Sad']['Value']
        cv2.rectangle(frame,
                      (int(face['BoundingBox']['Left']*width),
                       int(face['BoundingBox']['Top']*height)),
                      (int((face['BoundingBox']['Left']+face['BoundingBox']['Width'])*width),
                       int((face['BoundingBox']['Top']+face['BoundingBox']['Height'])*height)),
                      green if sad else red, frame_thickness)
        emothions = face['Emotions']
        i = 0
        for emothion in emothions:
            cv2.putText(frame,
                        str(emothion['Type']) + ": " + str(emothion['Confidence']),
                        (25, 40 + (i * 25)),
                        fontface,
                        fontscale,
                        color)
            i += 1
        else:
            pass


        if sad:
            myMQTTClient.publish("fyp/test", json.dumps({"status": "true"}), 0)
            pygame.mixer.music.load('voice.mp3')
            pygame.mixer.music.play(1)
            time.sleep(60)
            pygame.mixer.music.stop()
            break
        else:
            pass

    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


capture.release()
cv2.destroyAllWindows()