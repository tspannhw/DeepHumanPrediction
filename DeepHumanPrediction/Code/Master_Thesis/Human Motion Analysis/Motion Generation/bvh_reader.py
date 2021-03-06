# -*-coding: utf-8-*-
import numpy as np
import glob
from tqdm import *
import os
import sys

def Motion_Data_Preprocessing(time_step=100, seed_timestep=20, batch_Frame=5 ,TEST=False , Model=1):
    
    np.set_printoptions(threshold=1000000)

    if TEST==False:
        file_directory = glob.glob("Dataset/Training/*.bvh")
    else:
        file_directory = glob.glob("Dataset/Test/Model{}/*.bvh".format(Model))
        if file_directory == list():
            print("Data does not exist")
            sys.exit(0)

    time_step = time_step
    seed_timestep = seed_timestep
    batch_Frame = batch_Frame
    xyz_position = 3
    complexity = False
    Data = []
    train_label_motion = []

    '''data normalization'''
    Normalization_factor = 1
    dtype = "int"


    for file_name, i in tqdm(zip(file_directory, range(len(file_directory)))):
        # time.sleep(0.01)
        Raw = []
        Mdata = []
        MOTION = False
        '''1.basic -  Motion data preprocessing'''
        print('Processed Data : {}'.format(i + 1))
        try:
            with open(file_name, 'r') as f:
                while True:
                    line = f.readline()
                    if line == 'MOTION' + "\n" or MOTION:
                        MOTION = True
                        Raw.append(line)
                    if not line:
                        break
            for raw in Raw[3:]:
                # Xposition Yposition Zposition 는 제외
                if dtype == "int":
                    temp = raw.split()[xyz_position:]
                    if complexity:
                        temp = [np.float32(i) * Normalization_factor for i in temp]
                    else:  # complexity = False
                        temp = [np.floor(np.float32(i)) * Normalization_factor for i in temp]
                else:  # dtype="str"
                    temp = raw.split()[xyz_position:]
                Mdata.append(temp)
            # Remove the blank line..
            Mdata.pop()

            '''2. Motion data preprocessing - easy for deeplearning'''

            # data padding
            if len(Mdata) < time_step:
                frame = np.zeros(shape=(time_step - len(Mdata), len(Mdata[0])))
                for i in range(time_step - len(Mdata)):
                    frame[i] = Mdata[-1]
                Mdata = np.concatenate((Mdata, frame), axis=0)
            else:
                Mdata = Mdata[:time_step]
            Data.append(Mdata)
        except Exception as e:
            raise e

    '''3.final -  Motion data preprocessing'''
    for i in range(len(file_directory)):
        train_label_motion.append(Data[i][seed_timestep:])

    print("-------------------Data Shape--------------------")
    print("train_motion shape = {}".format(np.shape(Data)))
    print("train_label_motion shape = {}".format(np.shape(train_label_motion)))
    print("\n")

    train_motion = np.reshape(Data, (len(file_directory), int(time_step / batch_Frame), len(Data[0][0]) * batch_Frame))
    train_label_motion = np.reshape(train_label_motion, (len(file_directory), int((time_step-seed_timestep) / batch_Frame), len(Data[0][0]) * batch_Frame))

    print("-------------------Transform Data Shape--------------------")
    print("transform_motion shape = {}".format(np.shape(train_motion)))
    print("transform_label_motion shape = {}".format(np.shape(train_label_motion)))
    print("\n")

    return Normalization_factor, train_motion, train_label_motion, int(seed_timestep / batch_Frame), int(
        (time_step - seed_timestep) / batch_Frame), len(train_motion[0][0]), file_directory

if __name__ == "__main__":

    print('Motion_Data_Preprocessing_Starting In Main')
    Normalization_factor, train_motion, train_label_motion, seed_timestep, pre_timestep, column, file_directory = Motion_Data_Preprocessing(time_step=100, seed_timestep=20, batch_Frame=1 , TEST=False)

    print("new seed_timestep : {}".format(seed_timestep))
    print("new prediction_timestep : {}".format(pre_timestep))
    print("new Motion_rotation_data : {}".format(column))

else:
    print("Motion_Data_Preprocessing_Imported")
