import sys
sys.path.append('/home/pi/tflite1/tflite1-env/lib/python3.7/site-packages')
import os
import cv2
import numpy as np
from tflite_runtime.interpreter import Interpreter
from gpiozero import MotionSensor
from picamera import PiCamera
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="ana",
  database="baza"
)

mycursor = mydb.cursor()

mycursor.execute("CREATE TABLE IF NOT EXISTS brojac (id INT AUTO_INCREMENT PRIMARY KEY, broj INT)")

PIR = MotionSensor(17)
CAMERA = PiCamera()
cnt = 0

MODEL_NAME = "/home/pi/tflite1/Sample_TFLite_model"
GRAPH_NAME = "detect.tflite"
LABELMAP_NAME = "labelmap.txt"
min_conf_threshold = 0.5

CWD_PATH = os.getcwd()

PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,GRAPH_NAME)
PATH_TO_LABELS = os.path.join(CWD_PATH,MODEL_NAME,LABELMAP_NAME)

with open(PATH_TO_LABELS, 'r') as f:
    labels = [line.strip() for line in f.readlines()]
    
if labels[0] == '???':
    del(labels[0])

interpreter = Interpreter(model_path=PATH_TO_CKPT)

interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

floating_model = (input_details[0]['dtype'] == np.float32)

input_mean = 127.5
input_std = 127.5

while True:
    PIR.wait_for_motion()
    object_name = []
    print('Nesto se krece!')
    CAMERA.capture('image.jpg')
    image = cv2.imread('/home/pi/tflite1/image.jpg')
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    imH, imW, _ = image.shape
    image_resized = cv2.resize(image_rgb, (width, height))
    input_data = np.expand_dims(image_resized, axis=0)
    
    if floating_model:
        input_data = (np.float32(input_data) - input_mean) / input_std

    interpreter.set_tensor(input_details[0]['index'],input_data)
    interpreter.invoke()
    
    boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
    classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
    scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects

    for i in range(len(scores)):
        if ((scores[i] > min_conf_threshold) and (scores[i] <= 1.0)):
            object_name.append(labels[int(classes[i])])
    #print(object_name.count('person'))
        
    data = object_name.count('person')
    print(data)
    
    if data == 0:
        mycursor.execute("TRUNCATE TABLE brojac")
        mydb.commit()
    
    mycursor.execute("INSERT INTO brojac (broj) VALUES ({})".format(data))
    mydb.commit()    
    
    


    PIR.wait_for_no_motion()

      
