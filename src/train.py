#train.py

import os 
import argparse
import pandas as pd
import numpy as np 

from sklearn.model_selection    import train_test_split
from keras.models               import Sequential #its nothing but linear stack of layers
from keras.optimizers           import Adam 
from keras.callbacks            import ModelCheckpoint #to save model periodically as cehckpoints
from keras.layers               import Lambda, Conv2D, MaxPooling2D, Dropout, Dense, Flatten

from utils import INPUT_SHAPE,batch_generator
np.random.seed(0) 

def define_args():
    """
    Define an arg parser. Set default values to the input arguments.
    """
    parser = argparse.ArgumentParser(description='Behavioral Clonning Project')
    parser.add_argument('-d', help='Data directory',        dest='data_dir',      type=str,       default='../../data')
    parser.add_argument('-t', help='Test size fraction',    dest='test_size',     type=float,     default=0.2)
    parser.add_argument('-k', help='Drop out probability',  dest='keep_prob',     type=float,     default=0.5)
    parser.add_argument('-n', help='Number of epochs',      dest='nb_epoch',      type=int,       default=10)
    parser.add_argument('-s', help='Samples per epochs',    dest='samples_epoch', type=int,       default=20000)
    parser.add_argument('-b', help='Batch size',            dest='batch_size',    type=int,       default=40)
    parser.add_argument('-o', help='Save best models only', dest='save_best_only',type=str,       default='true')
    parser.add_argument('-l', help='Learning rate',         dest='learning_rate', type=float,     default=1.0e-4)
    args = parser.parse_args()
    return args

def print_input_params(args):
    """
    Print input parameters passed thru arg parser
    """
    print ('\n'*3)
    print ('_'*40)
    print('Parameters')
    print ('_'*40)
    for key,val in vars(args).items():
        print('{:<30} := {}'.format(key,val))
    print ('_'*40)

def load_data(args):
    """
    Read input csv data.

    The input drive data csv has instantanious steer angle, throttle, speed and corresponding frame names(for center, left and right camera views). 
    This file is generated by the udacity simulator while recording the run.
    """

    #read input csv data as pandas dataframe
    data = pd.read_csv(os.path.join(os.getcwd(), args.data_dir,'driving_log.csv'), names=['center', 'left','right','steering','throttle','reverse', 'speed'])

    #define input data
    X = data[['center', 'left', 'right']].values
    
    #define labeled/expected data
    y = data[['steering']].values

    #print sample data; printing first a few rows of the data
    print (data.head())

    #divide input data into train and validation sets
    X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=args.test_size, random_state=0)

    return X_train, X_valid, y_train, y_valid

def build_model(args):
    """
    Nvidia autonomous-driving network architecture is followed

    The network model is defined as follows:
    (Input image dimension is 3x66x200)
    1. Input image normalization 3x66x200
    2. Convoultion layer 24x31x98 @kernel 5x5
    3. Convoultion layer 36x14x47 @kernel 5x5
    4. Convoultion layer 48x 5x22 @kernel 5x5
    5. Convoultion layer 64x 3x20 @kernel 3x3
    6. Convoultion layer 64x 1x18 @kernel 3x3
    7. Flatten -> Fully connected layer 1164
    8. Fully connected layer 100
    9. Fully connected layer 50
    10.Fully connected layer 10
    11.Output layer 1
    read more here: https://devblogs.nvidia.com/deep-learning-self-driving-cars/
    """
    model = Sequential()
    model.add(Lambda(lambda x: x/127.5 - 1.0, input_shape=INPUT_SHAPE)) #data normalization operation
    model.add(Conv2D(24, 5,5, activation='elu', subsample=(2,2)))
    model.add(Conv2D(36, 5,5, activation='elu', subsample=(2,2)))
    model.add(Conv2D(48, 5,5, activation='elu', subsample=(2,2)))
    model.add(Conv2D(64, 3,3, activation='elu'))
    model.add(Conv2D(64, 3,3, activation='elu'))
    model.add(Dropout(args.keep_prob))
    model.add(Flatten())
    model.add(Dense(100, activation='elu'))
    model.add(Dense(50, activation='elu'))
    model.add(Dense(10, activation='elu'))
    model.add(Dense(1))
    model.summary()
    return model

def train_model(model, args, X_train, X_valid, y_train, y_valid):
    """
    Trains the classifier 

    I. Saves the model after every epoch.
    #monitor: quantity to monitor, 
    #verbose: verbosity i.e logging mode (0, 1 or 2), read more : https://stackoverflow.com/questions/47902295/what-is-the-use-of-verbose-in-keras-while-validating-the-model
    #save_best_only: if save_best_only is true the latest best model according to the quantity monitored will not be overwritten.
    #mode: one of {auto, min, max}. 
    #If save_best_only=True, the decision to overwrite the current save file is
    made based on either the maximization or the minimization of the monitored quantity. For val_acc, 
    this should be max, for val_loss this should be min, etc. In auto mode, the direction is automatically
    inferred from the name of the monitored quantity.
    
    II. Calculate the difference between expected steering angle and actual steering angle
    #square the difference add up all those differences for as many data points as we have
    #divide by the number of them that value is our mean squared error! this is what we want to minimize via gradient descent
    
    III. Fits the model on data generated batch-by-batch by a Python generator.
    #The generator is run in parallel to the model, for efficiency. 
    #For instance, this allows you to do real-time data augmentation on images on CPU in 
    #parallel to training your model on GPU.
    #so we reshape our data into their appropriate batches and train our model simulatenously
    """
    
    checkpoint = ModelCheckpoint ('model-{epoch:03d}.h5',
                                    monitor='val_loss',
                                    verbose=1,
                                    save_best_only=args.save_best_only,
                                    mode='auto')
    model.compile(loss='mean_squared_error', optimizer=Adam(lr=args.learning_rate))
    model.fit_generator(batch_generator(args.data_dir, X_train, y_train, args.batch_size, True),
                        args.samples_epoch,
                        args.nb_epoch,
                        max_q_size=1,
                        validation_data=batch_generator(args.data_dir,X_valid,y_valid,args.batch_size,False),
                        nb_val_samples=len(X_valid),
                        callbacks=[checkpoint],
                        verbose=0)

def main():
    args = define_args()
    print_input_params(args)
    data = load_data(args)
    model = build_model(args)
    train_model(model, args, *data)

if __name__ == "__main__":
    main()