#run.py

import os
import argparse
import shutil
import utils
import cv2
import numpy as np
from datetime import datetime
from keras.models import load_model

#packages related to simulator server connections
from io import BytesIO
from PIL import Image #image manipulation
import base64 #decoding camera images
import socketio #real-time server
import eventlet #concurrent networking 
import eventlet.wsgi #web server gateway interface
from flask import Flask #web framework

sio = socketio.Server() #initialize udacity-sim server
app = Flask(__name__) #our flask app

model = None #initialize model

MAX_SPEED = 15
MIN_SPEED = 10
speed_limit = MAX_SPEED

sw_img = None

def displaySteerWheel(steerAngle):
    global sw_img, sw_img_h, sw_img_w
    if sw_img== None:
        sw_img = cv2.imread('../assets/steerwheel.jpeg')
        (sw_img_h, sw_img_w) = sw_img.shape[:2]
        print (sw_img_h, sw_img_w)
    else:
        rot_angle = np.sign(steerAngle)*(steerAngle**2) * -1000.0 
        r_matrix = cv2.getRotationMatrix2D((sw_img.shape[1]/2, sw_img.shape[0]/2), rot_angle , 1)
        sw_img_rot = cv2.warpAffine(sw_img, r_matrix, (sw_img_h, sw_img_w),borderValue=(255,255,255))
        cv2.imshow("Steering Wheel", sw_img_rot)
        cv2.waitKey(1)

def displayInputVideo(img):
    win_name = "Vehicle Front View"
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    cv2.imshow(win_name, img)
    cv2.waitKey(1)


@sio.on('telemetry')
def telemetry(sid, data):
    """
    Registering event handler for the server
    """
    if data:
        #current status parameters of the car
        steering_angle  = float(data["steering_angle"]) 
        speed           = float(data["speed"])
        # throttle        = float(data["throttle"])
        image           = Image.open(BytesIO(base64.b64decode(data["image"])))
        

        try:
            image       = np.asarray(image)       #from PIL Image format to np array
            image_disp  = image.copy()
            image       = utils.preprocess(image) #input preprocessing
            image       = np.array([image])       #the model expects 4D array

            #predict steer angle
            steering_angle = float(model.predict(image, batch_size=1))

            #lower throttle as speed increases
            global speed_limit
            
            if speed > speed_limit:
                speed_limit = MIN_SPEED #slowdown
            else:
                speed_limit = MAX_SPEED
            throttle = 1.0 - steering_angle**2 - (speed/speed_limit)**2
            print('{} {} {}'.format(steering_angle, throttle, speed))
            send_control(steering_angle, throttle)

            displaySteerWheel(steering_angle)
            displayInputVideo(image_disp)

        except Exception as e:
            print(e)

        #dump images
        if args.image_folder != '':
            timestamp = datetime.utcnow().strftime('%y_%m_%d_%h_%m_%s_%f')[:-3]
            image_fileName = os.path.join(args.image_folder, timestamp)
            image.save('{}.jpg'.format(image_fileName))
    else:
        sio.emit('manual', data={}, skip_sid=True)

@sio.on('connect')
def connect(sid, environ):
    """
    Connect to server
    """
    print ("connect ", sid)
    send_control(0,0)

def send_control(steering_angle, throttle):
    """
    Send commands to the simulator server
    """
    sio.emit(
            "steer", 
            data= {
                'steering_angle'    : steering_angle.__str__(),
                'throttle'          : throttle.__str__()
            },
            skip_sid=True)

if __name__ == '__main__':
    """
    Main funtion
    """
    DEFAULT_MODEL = './model-000.h5'

    parser = argparse.ArgumentParser(description='Automatic Driving')
    parser.add_argument('-m', dest='model',        type = str, nargs='?',   default='', help = 'Path to model h5 file. Model should be on the same path.')
    parser.add_argument('-i', dest='image_folder', type=str,   nargs='?',   default='', help= 'Path to image folder. This is wher the images from the run will be saved.')
    args = parser.parse_args()


    #load the model file
    if args.model != '':
        model = load_model(args.model)
    else:
        model = load_model(DEFAULT_MODEL)

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
    
    # global app
    #wrap Flask application with engineio's middleware
    app = socketio.Middleware(sio, app)

    #deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app)

    cv2.destroyAllWindows()