#run.py

import os
import argparse
import shutil
import utils
import numpy as np
from io import BytesIO
from datetime import datetime
from PIL import Image #image manipulation
from keras.models import load_model
#decoding camera images
import base64

import socketio #real-time server
import eventlet #concurrent networking 
import eventlet.wsgi #web server gateway interface
from flask import Flask #web framework

sio = socketio.Server() #initialize udacity-sim server
app = Flask(__name__) #our flask app

model = None #initialize model
prev_image_array = None #initialize image array
MAX_SPEED = 15
MIN_SPEED = 10
speed_limit = MAX_SPEED

#registering event handler for the server
@sio.on('telemetry')
def telemetry(sid, data):
    if data:
        #current status parameters of the car
        steering_angle  = float(data["steering_angle"]) 
        throttle        = float(data["throttle"])
        speed           = float(data["speed"])
        image           = Image.open(BytesIO(base64.b64decode(data["image"])))

        try:
            image = np.asarray(image)       #from PIL Image format to np array
            image = utils.preprocess(image) #input preprocessing
            image = np.array([image])       #the model expects 4D array

            #predict steer angle
            steering_angle = float(model.predict(image, batch_size=1))

            #lower throttle as speed increases
            global speed_limit
            
            # if speed > (speed_limit):
            #     speed_limit = (speed_pred) #slowdown
            # else:
            #     speed_limit = max(speed_pred, 2.0)
            # throttle = 1.0 - (speed/speed_limit)**2
            # if throttle < 0.1:
            #     throttle = 0.1

            
            if speed > speed_limit:
                speed_limit = MIN_SPEED #slowdown
            else:
                speed_limit = MAX_SPEED
            throttle = 1.0 - steering_angle**2 - (speed/speed_limit)**2
            print('{} {} {}'.format(steering_angle, throttle, speed))
            send_control(steering_angle, throttle)
        except Exception as e:
            print(e)

        #dump images
        if args.image_folder != '':
            timestamp = datetime.utcnow().strftime('%y_%m_%d_%h_%m_%s_%f')[:-3]
            image_fileName = os.path.join(args.image_folder, timestamp)
            image.save('{}.jpg'.format(image_fileName))
    else:
        sio.emit('manual', data={}, skip_sid=True)

#connect to server
@sio.on('connect')
def connect(sid, environ):
    print ("connect ", sid)
    send_control(0,0)

#send commands to server
def send_control(steering_angle, throttle):
    sio.emit(
            "steer", 
            data= {
                'steering_angle'    : steering_angle.__str__(),
                'throttle'          : throttle.__str__()
            },
            skip_sid=True)

# def main():
#     parser = argparse.ArgumentParser(description='Automatic Driving')
#     parser.add_argument('model',        type = str,     default='./model-008.h5',  help = 'Path to model h5 file. Model should be on the same path.')
#     parser.add_argument('image_folder', type=str,       nargs='?',  default='', help= 'Path to image folder. This is wher the images from the run will be saved.')
#     args = parser.parse_args()

#     #load the model file
#     model = load_model(args.model)

#     if(args.image_folder !=''):
#         print("Creating image folder at {}".format(args.image_folder))
#         if not os.path.exists(args.image_folder):
#             os.makedirs(args.image_folder)
#         else:
#             shutil.rmtree(args.image_folder)
#             os.makedirs(args.image_folder)
#         print("Recording this run..")
#     else:
#         print("Not recording this run..")
    
#     #wrap Flask application witj engineio's middleware
#     global app
#     app = socketio.Middleware(sio, app)

#     #deploy as an eventlet WSGI server
#     eventlet.wsgi.server(eventlet.listen(('',4567), app))

if __name__ == '__main__':
    # main()
    parser = argparse.ArgumentParser(description='Automatic Driving')
    # parser.add_argument('model',        type = sstr,  help = 'Path to model h5 file. Model should be on the same path.')
    parser.add_argument('image_folder', type=str,       nargs='?',  default='', help= 'Path to image folder. This is wher the images from the run will be saved.')
    args = parser.parse_args()

    #load the model file
    # model = load_model(args.model)
    model = load_model('./model-005.h5')
    # model2 = load_model('./speed_model.h5')

    if(args.image_folder !=''):
        print("Creating image folder at {}".format(args.image_folder))
        if not os.path.exists(args.image_folder):
            os.makedirs(args.image_folder)
        else:
            shutil.rmtree(args.image_folder)
            os.makedirs(args.image_folder)
        print("Recording this run..")
    else:
        print("Not recording this run..")
    
    #wrap Flask application with engineio's middleware
    # global app
    app = socketio.Middleware(sio, app)

    #deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app)