# -*- coding: utf-8 -*-
"""Untitled4.ipynb

Automatically generated by Colaboratory.

"""

#!/usr/bin/env python3.7   # To run the file using ./predictor.py
import os
import sys
import logging

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'   # to supress warnings.
# Keras outputs warnings using `print` to stderr so let's direct that to devnull temporarily
#stderr = sys.stderr
#sys.stderr = open(os.devnull, 'w')   # sending error to null
'''
./predictor.py -j $job_name -o $1 -a $activations -p $parameters -i $input -g $gpu_2070s    # input 
'''

import argparse
import joblib
from sklearn.datasets import load_iris
import warnings
warnings.filterwarnings("ignore")

import torch
import torchvision
import torch.nn as nn
import numpy as np
import math
from class_cnn import CNN

parser = argparse.ArgumentParser(description='Summary Tool & Coordinated Predictions.')
parser.add_argument('-m', '--model', default='resnet18', help='model name')
parser.add_argument('-b', '--batchsize', default='64', help='batchsize')
parser.add_argument('-o', '--operation', default='trainingg', help='mode of operation')
parser.add_argument('-g', '--gpu', default='2070s', help='specify gpu')
args = parser.parse_args()

ip = (3, 224, 224)
batch_size = args.batchsize
batchsize1 = float(batch_size)

if "vgg11" in args.model:
  model = torch.hub.load('pytorch/vision:v0.10.0', 'vgg11', pretrained=True)
if "vgg13" in args.model:
  model = torch.hub.load('pytorch/vision:v0.10.0', 'vgg13', pretrained=True)
if "vgg16" in args.model:
  model = torch.hub.load('pytorch/vision:v0.10.0', 'vgg16', pretrained=True)
if "vgg19" in args.model:
  model = torch.hub.load('pytorch/vision:v0.10.0', 'vgg19', pretrained=True)
if "resnet18" in args.model:
  model = torchvision.models.resnet18(pretrained=True, progress=True)
if "resnet34" in args.model:
  model = torchvision.models.resnet34(pretrained=True, progress=True)
if "resnet50" in args.model:
  model = torchvision.models.resnet50(pretrained=True, progress=True)
if "resnet101" in args.model:
  model = torchvision.models.resnet101(pretrained=True, progress=True)
if "resnet152" in args.model:
  model = torchvision.models.resnet152(pretrained=True, progress=True)
if "densenet121" in args.model:
  model = torch.hub.load('pytorch/vision:v0.10.0', 'densenet121', pretrained=True)
if "densenet169" in args.model:
  model = torch.hub.load('pytorch/vision:v0.10.0', 'densenet169', pretrained=True)
if "densenet201" in args.model:
  model = torch.hub.load('pytorch/vision:v0.10.0', 'densenet201', pretrained=True)

obj = CNN(model, ip, batchsize1)
x = obj.main()

def predictor1(jobname, option, activations, parameters, inputsize, gpu):
    #GPUs in the cluster
    #CUDA_cores,MemoryBW_GBps,Memory_clock_speed_MHz,Tensor_cores,SM_count
    gpu_2070s=[2560,448,14000,320,40]
    gpu_3070=[5888,512,16000,184,46]
    gpu_3080=[8704,760.3,19000,272,68]
    gpu_3090=[5120,900,1752,640,80]
    '''
    parser = argparse.ArgumentParser(description='Loading predictors and returning prediction.')
    parser.add_argument('-j', '--jobname', help='Job name')
    parser.add_argument('-o', '--option', help='option either 1 or 2')
    parser.add_argument('-a', '--activations', help='Model activations')
    parser.add_argument('-p', '--parameters', help='Model parameters')
    parser.add_argument('-i', '--inputsize', help='Model input size')
    parser.add_argument('-g', '--gpu', help='GPU either 2070s or 3070 or 3090')
    args = parser.parse_args()
    
    print(args.jobname)
    print(args.option)
    print(args.activations)
    print(args.parameters)
    print(args.inputsize)
    print(args.gpu)
    '''

    if gpu == "2070s":
        gpu = gpu_2070s
    elif gpu == "3070":
        gpu = gpu_3070
    elif gpu == "3080":
        gpu = gpu_3080
    elif gpu == "3090":
        gpu = gpu_3090

    if option == "1":
        #print("option 1")
        if "trainingg" in jobname:
            #print("train job")
            train_mem_pred=joblib.load("./train_mem_RFR_3params.joblib")
            print(train_mem_pred)
            ##CUDA_cores,MemoryBW_GBps,Memory_clock_speed_MHz,Tensor_cores,SM_count
            #X = df[['activations', 'parameters','input','Memory bandwidth (GB/s)','Pipelines/CUDA cores', 'SM count']]
            tm = train_mem_pred.predict([[float(activations),float(parameters),float(inputsize),gpu[1],gpu[0],gpu[4]]])
            if tm.shape == (1,):
                tain_mem = tm[0]
            elif tm.shape == (1,1):
                tain_mem = tm[0,0]
            train_time_pred=joblib.load("random_forest_inferTime_combined.joblib")
            ##CUDA_cores,MemoryBW_GBps,Memory_clock_speed_MHz,Tensor_cores,SM_count
            #X = df[['activations', 'parameters','input','Pipelines/CUDA cores', 'Memory bandwidth (GB/s)', 'SM count','Memory clock speed (MHz)','Tensor cores']]
            tt = train_time_pred.predict([[activations,parameters,gpu[0],gpu[1],gpu[4],gpu[2],gpu[3]]])
            if tt.shape == (1,):
                train_time = tt[0]
            elif tt.shape == (1,1):
                train_time = tt[0,0]
            print("Peak GPU memory predicted for training in MB:", "%f" % tain_mem)
            print("Job Completion time predicted for training in seconds:", "%f" % train_time)
            #print("%f,%f" % (tain_mem,train_time))

        ##inference-vgg19-cat2
        if "inference" in jobname:
            infer_mem_pred=joblib.load("infer_mem_RFR_5params.joblib")
            #X = df[['activations', 'parameters', 'Memory bandwidth (GB/s)','Pipelines/CUDA cores', 'SM count', 'Memory clock speed (MHz)','Tensor Cores (GPU)']]
            im = infer_mem_pred.predict([[float(activations),float(parameters),gpu[1],gpu[0],gpu[4],gpu[2],gpu[3]]])
            if im.shape == (1,):
                infer_mem = im[0]
            elif im.shape == (1,1):
                infer_mem = im[0,0]

            infer_time_pred=joblib.load("Final_TrainingTime_random_forest.joblib")
            it = infer_time_pred.predict([[float(activations),float(parameters),inputsize,gpu[1],gpu[0],gpu[4],gpu[2],gpu[3]]])
            if it.shape == (1,):
                infer_time = it[0]
            elif it.shape == (1,1):
                infer_time = it[0,0]
            print("Peak GPU memory predicted for inference in MB:", "%f" % infer_mem)
            print("Job Completion time predicted for inference in seconds:", "%f" % infer_time)
            #print("%f,%f" % (infer_mem,infer_time))


    elif option == "2":
        if "trainingg" in jobname:
            train_mem_pred=joblib.load("train_mem_RFR_5params.joblib")
            ##CUDA_cores,MemoryBW_GBps,Memory_clock_speed_MHz,Tensor_cores,SM_count
            #X = df[['activations', 'parameters','input', 'Memory bandwidth (GB/s)', 'Pipelines/CUDA cores','SM count','Memory clock speed (MHz)','Tensor cores']]
            tm = train_mem_pred.predict([[float(activations),float(parameters),float(inputsize),gpu[1],gpu[0],gpu[4],gpu[2],gpu[3]]])
            if tm.shape == (1,):
                tain_mem = tm[0]
            elif tm.shape == (1,1):
                tain_mem = tm[0,0]
            train_time_pred=joblib.load("infer_time_RFR_3params.joblib")
            ##CUDA_cores,MemoryBW_GBps,Memory_clock_speed_MHz,Tensor_cores,SM_count
            #X = df[['activations', 'parameters','input','Pipelines/CUDA cores', 'Memory bandwidth (GB/s)', 'SM count','Memory clock speed (MHz)','Tensor cores']]
            tt = train_time_pred.predict([[float(activations),float(parameters),float(inputsize),gpu[0],gpu[1],gpu[4],gpu[2],gpu[3]]])
            if tt.shape == (1,):
                train_time = tt[0]
            elif tt.shape == (1,1):
                train_time = tt[0,0]
            print("%f,%f" % (tain_mem,train_time))


        if "inference" in jobname:
            infer_mem_pred=joblib.load("infer_mem_RFR_3params.joblib")
            #X = df[['activations', 'parameters', 'Memory bandwidth (GB/s)','Pipelines/CUDA cores', 'SM count']]
            im = infer_mem_pred.predict([[float(activations),float(parameters),gpu[1],gpu[0],gpu[4]]])
            if im.shape == (1,):
                infer_mem = im[0]
            elif im.shape == (1,1):
                infer_mem = im[0,0]

            infer_time_pred=joblib.load("train_time_RFR_5params.joblib")
            #X = df[['activations', 'parameters', 'Memory bandwidth (GB/s)','Pipelines/CUDA cores', 'SM count']]
            it = infer_time_pred.predict([[float(activations),float(parameters),gpu[1],gpu[0],gpu[4]]])
            if it.shape == (1,):
                infer_time = it[0]
            elif it.shape == (1,1):
                infer_time = it[0,0]
            print("%f,%f" % (infer_mem,infer_time))

predictor1(args.operation, "1", x[0], x[1], x[2], args.gpu)