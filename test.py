import sys
sys.path.append('/home/pi/tflite1/tflite1-env/lib/python3.7/site-packages')
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="raspberry"
)

print(mydb)