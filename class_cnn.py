# -*- coding: utf-8 -*-
"""Untitled2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1amRqLZSnhTxMWXPuxrN7QgHeEPjsOY9p
"""

import torch
import torchvision
import torch.nn as nn
import numpy as np
import math

class CNN:
  def __init__(self,model,input,batch_size):
    self.model = model
    self.input = input
    self.batch_size = batch_size
    self.count = 0
    self.in_tensor = [batch_size, self.input[0], self.input[1], self.input[2]]
    self.out_tensor = []
    self.total_para = 0
    self.total_act = 0
    self.initial_path = ['parent', 'child']
    self.path = []
    self.list1 = []
    

  def main(self):
    model_children = list(self.model.children())
    for i in range (len(model_children)):   #execute 3 times 1.sequential 2.ada 3.linear
      self.path.append((type(model_children[i]).__name__)+str(i))
      self.traversal(model_children[i])
      self.path = []
    print("\n","Overall Summary:")
    print("Input Size(MB):", ((np.prod(self.input) * self.batch_size)*4)/(1024**2))
    print("Total parameters(MB):",  (self.total_para* 4) / (1024**2))
    print("Total Activations(MB):",  (self.total_act* 4) / (1024**2))
    input_final = ((np.prod(self.input) * self.batch_size) * 4) / (1024 ** 2)
    parameter_final = (self.total_para* 4) / (1024**2)
    activation_final = (self.total_act* 4) / (1024**2)
    self.list1 = [activation_final,parameter_final,input_final]
    return self.list1

  
  def traversal(self,model_children):
    list_child = list(model_children.children())
    if not list_child:      #list_child is empty
      #print("path", self.path)
      self.all_layers(model_children, self.input, self.batch_size, self.in_tensor, self.path)
      self.path.pop()
    else:
      for j in range(len(list_child)):
        self.path.append((type(list_child[j]).__name__))
        self.traversal(list_child[j])
      self.path.pop()
    
  def all_layers(self,child, input, batch_size, in_tensor, local_path):
    
    input_size = input #value is touple(c,n,n)
    batch_size = batch_size #value is 'int'(between 1 to 64)
    i1 = 0
    i2 = 0
    if len(in_tensor)>2:
      i1 = in_tensor[2]
      i2 = in_tensor[3]
    #print("in_tensor:",in_tensor)
    #print("initial path:",self.initial_path)
    #print("local path:",local_path)
    

    if local_path[0] == self.initial_path[0]:
      if local_path[1] == self.initial_path[1]:
        if type(child) == nn.Conv2d:  #(in_channels, out_channels, kernel_size=(), stride=(), padding=(),bias=True) (int or touple)
          #parameters
          parameters = (child.weight.shape[0]*child.weight.shape[1]*child.weight.shape[2]*child.weight.shape[3])+ child.weight.shape[0]
          if child.bias is None:
            parameters =  parameters - child.weight.shape[0]
          para_mem = (parameters * 4) / (1024**2)
          self.total_para += parameters
          #activations
          self.out_tensor = [batch_size, child.out_channels, in_tensor[2], in_tensor[3]]
          size_out_tensor = batch_size * child.out_channels * in_tensor[2] * in_tensor[3]
          mem_out_tensor = (size_out_tensor * 4) / (1024**2)
          self.total_act += size_out_tensor

          self.count +=1
          #print(self.count, child)
      
        elif type(child) == nn.ReLU: #(inplace=True) Inplace true means operations will perform in place to save memory. Default value is false.
          #if child.inplace == False:
          self.out_tensor = in_tensor.copy()
          size_out_tensor = np.prod(self.out_tensor)
          mem_out_tensor = (size_out_tensor * 4) / (1024**2)
          #self.total_act += size_out_tensor
          #else:
            #mem_out_tensor = 0
            #self.out_tensor = in_tensor
          
          self.count +=1
          #print(self.count,child)
        
        elif type(child) == nn.MaxPool2d: #(kernel_size(int), stride(int), padding(int), dilation(int), ceil_mode=False)
          i1 = math.ceil(((i1 + (2*child.padding)-child.dilation) - child.kernel_size)/child.stride) + 1
          i2 = math.ceil(((i2 + (2*child.padding)-child.dilation) - child.kernel_size)/child.stride) + 1
          self.out_tensor = [batch_size, in_tensor[1], int(i1), int(i2)]
          size_out_tensor = np.prod(self.out_tensor)
          mem_out_tensor = (size_out_tensor * 4) / (1024**2)
          self.total_act += size_out_tensor

          self.count +=1
          #print(self.count,child)

        elif type(child) == nn.AvgPool2d : #(kernel_size(int), stride(int), padding(int), dilation(int), ceil_mode=False)
          i1 = i1/child.kernel_size
          i2 = i2/child.kernel_size
          self.out_tensor = [batch_size, in_tensor[1], int(i1), int(i2)]
          size_out_tensor = np.prod(self.out_tensor)
          mem_out_tensor = (size_out_tensor * 4) / (1024**2)
          self.total_act += size_out_tensor

          self.count +=1
          #print(self.count,child)
        
        elif type(child) == nn.AdaptiveAvgPool2d: #(output_size=())
          self.out_tensor = [batch_size, in_tensor[1],child.output_size[0], child.output_size[1]]
          size_out_tensor = np.prod(self.out_tensor)
          mem_out_tensor = (size_out_tensor * 4) / (1024**2)
          self.total_act += size_out_tensor

          self.count +=1
          #print(self.count,child)
        
        elif type(child) == nn.BatchNorm2d: #(num_features, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
          #parameters
          parameters = (child.num_features * 2)   
          para_mem = (parameters * 4) / (1024**2)
          self.total_para += parameters
          #activations
          self.out_tensor = [batch_size,child.num_features, in_tensor[2],in_tensor[3]]
          size_out_tensor = np.prod(self.out_tensor)
          mem_out_tensor = (size_out_tensor * 4) / (1024**2)
          self.total_act += size_out_tensor

          self.count +=1
          #print(self.count,child)
        
        elif type(child) == nn.Linear: #(in_features, out_features, bias=True)
          #parameters
          parameters = (child.in_features * child.out_features) + child.out_features   
          para_mem = (parameters * 4) / (1024**2)
          self.total_para += parameters
          #activations
          self.out_tensor = [batch_size, child.out_features]
          size_out_tensor = np.prod(self.out_tensor)
          mem_out_tensor = (size_out_tensor * 4) / (1024**2)
          self.total_act += size_out_tensor

          self.count +=1
          #print(self.count,child)
        
        elif type(child) == nn.Dropout: #(p=0.5, inplace=False)
          P = child.p
          self.out_tensor = in_tensor.copy()
          size_out_tensor = (np.prod(self.out_tensor))/P
          mem_out_tensor = (size_out_tensor * 4) / (1024**2)
          self.total_act += size_out_tensor

          self.count +=1
          #print(self.count,child)

      else:
        if type(child) == nn.Conv2d:  #(in_channels, out_channels, kernel_size=(), stride=(), padding=(),bias=True) (int or touple)
          #parameters
          parameters = (child.weight.shape[0]*child.weight.shape[1]*child.weight.shape[2]*child.weight.shape[3])+ child.weight.shape[0]
          if child.bias is None:
            parameters =  parameters - child.weight.shape[0]
          para_mem = (parameters * 4) / (1024**2)
          self.total_para += parameters
          #activations
          i1 = (((i1 + (2*child.padding[0])) - child.kernel_size[0])/child.stride[0]) + 1
          i2 = (((i2 + (2*child.padding[0])) - child.kernel_size[0])/child.stride[0]) + 1 
          self.out_tensor = [batch_size, child.out_channels, int(i1), int(i2)]
          size_out_tensor = batch_size * child.out_channels * int(i1) * int(i2)
          mem_out_tensor = (size_out_tensor * 4) / (1024**2)
          self.total_act += size_out_tensor
          
          self.count +=1
          #print(self.count, child)
        
        elif type(child) == nn.ReLU: #(inplace=True) Inplace true means operations will perform in place to save memory. Default value is false.
          #if child.inplace == False:
          self.out_tensor = in_tensor.copy()
          size_out_tensor = np.prod(self.out_tensor)
          mem_out_tensor = (size_out_tensor * 4) / (1024**2)
          #else:
            #mem_out_tensor = 0
            #self.out_tensor = in_tensor
          #self.total_act += size_out_tensor

          self.count +=1
          #print(self.count,child)
        
        elif type(child) == nn.MaxPool2d: #(kernel_size(int), stride(int), padding(int), dilation(int), ceil_mode=False)
          i1 = math.ceil(((i1 + (2*child.padding)-child.dilation) - child.kernel_size)/child.stride) + 1
          i2 = math.ceil(((i2 + (2*child.padding)-child.dilation) - child.kernel_size)/child.stride) + 1
          self.out_tensor = [batch_size, in_tensor[1], int(i1), int(i2)]
          size_out_tensor = np.prod(self.out_tensor)
          mem_out_tensor = (size_out_tensor * 4) / (1024**2)
          self.total_act += size_out_tensor

          self.count +=1
          #print(self.count,child)

        elif type(child) == nn.AvgPool2d : #(kernel_size(int), stride(int), padding(int), dilation(int), ceil_mode=False)
          i1 = i1/child.kernel_size
          i2 = i2/child.kernel_size
          self.out_tensor = [batch_size, in_tensor[1], int(i1), int(i2)]
          size_out_tensor = np.prod(self.out_tensor)
          mem_out_tensor = (size_out_tensor * 4) / (1024**2)
          self.total_act += size_out_tensor

          self.count +=1
          #print(self.count,child)
        
        elif type(child) == nn.AdaptiveAvgPool2d: #(output_size=())
          self.out_tensor = [batch_size, in_tensor[1],child.output_size[0], child.output_size[1]]
          size_out_tensor = np.prod(self.out_tensor)
          mem_out_tensor = (size_out_tensor * 4) / (1024**2)
          self.total_act += size_out_tensor

          self.count +=1
          #print(self.count,child)
        
        elif type(child) == nn.BatchNorm2d: #(num_features, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
          #parameters
          parameters = (child.num_features * 2)   
          para_mem = (parameters * 4) / (1024**2)
          self.total_para += parameters
          #activations
          self.out_tensor = [batch_size,child.num_features, in_tensor[2],in_tensor[3]]
          size_out_tensor = np.prod(self.out_tensor)
          mem_out_tensor = (size_out_tensor * 4) / (1024**2)
          self.total_act += size_out_tensor

          self.count +=1
          #print(self.count,child)
        
        elif type(child) == nn.Linear: #(in_features, out_features, bias=True)
          #parameters
          parameters = (child.in_features * child.out_features) + child.out_features   
          para_mem = (parameters * 4) / (1024**2)
          self.total_para += parameters
          #activations
          self.out_tensor = [batch_size, child.out_features]
          size_out_tensor = np.prod(self.out_tensor)
          mem_out_tensor = (size_out_tensor * 4) / (1024**2)
          self.total_act += size_out_tensor

          self.count +=1
          #print(self.count,child)
        
        elif type(child) == nn.Dropout: #(p=0.5, inplace=False)
          P = child.p
          self.out_tensor = in_tensor.copy()
          size_out_tensor = (np.prod(self.out_tensor))/P
          mem_out_tensor = (size_out_tensor * 4) / (1024**2)
          self.total_act += size_out_tensor

          self.count +=1
          #print(self.count,child)

    else:
      if type(child) == nn.Conv2d:  #(in_channels, out_channels, kernel_size=(), stride=(), padding=(),bias=True) (int or touple)
        #parameters
        parameters = (child.weight.shape[0]*child.weight.shape[1]*child.weight.shape[2]*child.weight.shape[3])+ child.weight.shape[0]
        if child.bias is None:
          parameters =  parameters - child.weight.shape[0]
        para_mem = (parameters * 4) / (1024**2)
        self.total_para += parameters
        #activations
        i1 = (((i1 + (2*child.padding[0])) - child.kernel_size[0])/child.stride[0]) + 1
        i2 = (((i2 + (2*child.padding[0])) - child.kernel_size[0])/child.stride[0]) + 1 
        self.out_tensor = [batch_size, child.out_channels, int(i1), int(i2)]
        size_out_tensor = batch_size * child.out_channels * int(i1) * int(i2)
        mem_out_tensor = (size_out_tensor * 4) / (1024**2)
        self.total_act += size_out_tensor
        
        self.count +=1
        #print(self.count, child)
      
      elif type(child) == nn.ReLU: #(inplace=True) Inplace true means operations will perform in place to save memory. Default value is false.
        #if child.inplace == False:
        self.out_tensor = in_tensor.copy()
        size_out_tensor = np.prod(self.out_tensor)
        mem_out_tensor = (size_out_tensor * 4) / (1024**2)
        #else:
          #mem_out_tensor = 0
          #self.out_tensor = in_tensor
        #self.total_act += size_out_tensor
        
        self.count +=1
        #print(self.count,child)
      
      elif type(child) == nn.MaxPool2d: #(kernel_size(int), stride(int), padding(int), dilation(int), ceil_mode=False)
        i1 = math.ceil(((i1 + (2*child.padding)-child.dilation) - child.kernel_size)/child.stride) + 1
        i2 = math.ceil(((i2 + (2*child.padding)-child.dilation) - child.kernel_size)/child.stride) + 1
        self.out_tensor = [batch_size, in_tensor[1], int(i1), int(i2)]
        size_out_tensor = np.prod(self.out_tensor)
        mem_out_tensor = (size_out_tensor * 4) / (1024**2)
        self.total_act += size_out_tensor

        self.count +=1
        #print(self.count,child)

      elif type(child) == nn.AvgPool2d : #(kernel_size(int), stride(int), padding(int), dilation(int), ceil_mode=False)
        i1 = i1/child.kernel_size
        i2 = i2/child.kernel_size
        self.out_tensor = [batch_size, in_tensor[1], int(i1), int(i2)]
        size_out_tensor = np.prod(self.out_tensor)
        mem_out_tensor = (size_out_tensor * 4) / (1024**2)
        self.total_act += size_out_tensor

        self.count +=1
        #print(self.count,child)
      
      elif type(child) == nn.AdaptiveAvgPool2d: #(output_size=())
        self.out_tensor = [batch_size, in_tensor[1],child.output_size[0], child.output_size[1]]
        size_out_tensor = np.prod(self.out_tensor)
        mem_out_tensor = (size_out_tensor * 4) / (1024**2)
        self.total_act += size_out_tensor

        self.count +=1
        #print(self.count,child)
      
      elif type(child) == nn.BatchNorm2d: #(num_features, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        #parameters
        parameters = (child.num_features * 2)   
        para_mem = (parameters * 4) / (1024**2)
        self.total_para += parameters
        #activations
        self.out_tensor = [batch_size,child.num_features, in_tensor[2],in_tensor[3]]
        size_out_tensor = np.prod(self.out_tensor)
        mem_out_tensor = (size_out_tensor * 4) / (1024**2)
        self.total_act += size_out_tensor

        self.count +=1
        #print(self.count,child)
      
      elif type(child) == nn.Linear: #(in_features, out_features, bias=True)
        #parameters
        parameters = (child.in_features * child.out_features) + child.out_features   
        para_mem = (parameters * 4) / (1024**2)
        self.total_para += parameters
        #activations
        self.out_tensor = [batch_size, child.out_features]
        size_out_tensor = np.prod(self.out_tensor)
        mem_out_tensor = (size_out_tensor * 4) / (1024**2)
        self.total_act += size_out_tensor

        self.count +=1
        #print(self.count,child)
      
      elif type(child) == nn.Dropout: #(p=0.5, inplace=False)
        P = child.p
        self.out_tensor = in_tensor.copy()
        size_out_tensor = (np.prod(self.out_tensor))/P
        mem_out_tensor = (size_out_tensor * 4) / (1024**2)
        self.total_act += size_out_tensor

        self.count +=1
        #print(self.count,child)

    
    print("out tensor:", self.out_tensor, "-->", (type(child).__name__))
    self.in_tensor = self.out_tensor
    self.initial_path = local_path.copy()