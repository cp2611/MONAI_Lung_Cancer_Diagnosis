# -*- coding: utf-8 -*-
"""sreamlit_lung_cancer.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1sw0GW4h_1IuuPM8Mgbgl4UjMRFJfeceW
"""
import numpy as np
import streamlit as st
import pickle
import torch
import torchvision
import torch.nn as nn
from torchvision import transforms
 
import cv2
from PIL import Image,ImageOps
import dill as dill
sm=torch.nn.Softmax()

st.set_page_config(layout="wide")
page_bg_img = '''
<style>
body {
background-image: url("https://i.imgur.com/D0IOa1W.jpg?format=png");
background-size: cover;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)


st.title("""
Lung Cancer Prediction from X-Ray image
""")

st.write("""
Lung cancer, also known as lung carcinoma, is a malignant lung tumor characterized
by uncontrolled cell growth in tissues of the lung. This growth can spread
beyond the lung by the process of metastasis into nearby tissue or other parts of the body. Most
cancers that start in the lung, known as primary lung cancers, are carcinomas. \n
In the United States, lung cancer is the second most common cancer in both men and women.
It’s also the leading cause of death from cancer.
If lung cancer is found at an earlier stage, when it is small and before it has spread, it is more likely to be successfully treated.

### The standard digital image database with and without chest lung nodules (JSRT database) was created by the Japanese Society of Radiological Technology (JSRT) in cooperation with the Japanese Radiological Society (JRS) in 1998.

#### Tumors can be benign (noncancerous) or malignant (cancerous). Benign tumors tend to grow slowly and do not spread. Malignant tumors can grow rapidly, invade and destroy nearby normal tissues, and spread throughout the body. Benign tumor is considered is Normal as they are not cancerous.
 """)

img = cv2.imread(r'JPCLN009.png',0)  
img=Image.fromarray(img)

c2 ,c3  = st.beta_columns(( 0.3, 0.3))
c2.header("Malignant")
c3.header("Normal")
c2.image(img, use_column_width=True)
imgc2 = cv2.imread(r'JPCLN060.png',0)  
imgc2=Image.fromarray(imgc2)
c3.image(imgc2, use_column_width=True)


c5, c6,  = st.beta_columns(( 2, 1))
c5.header('User Input image')
c5.markdown("""
[Sample image](img)""")
c5.button("Upload your X-Ray below")
uploaded_file=c5.file_uploader("", type = ["png"])
#uploaded_image = Image.open(uploaded_file)
transformations_new=transforms.Compose([
    transforms.Resize(255),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=torch.tensor(0.5950) , std=torch.tensor(0.2735))
])
if uploaded_file is not None:
  uploaded_image=ImageOps.grayscale(Image.open(uploaded_file))
  input_new=  transformations_new(uploaded_image)
  input_new=input_new.unsqueeze(0)
  input_image=transforms.Resize(255)(uploaded_image)
else :
  input_image=transforms.Resize(255)(img)
  input_new=transforms.CenterCrop(224)(transforms.ToTensor()(input_image))
  input_new=input_new.unsqueeze(0)


if uploaded_file is not None:
  c6.image(input_image,channel='BGR')
else:
    c6.button("""Awaiting X_ray image to be uploaded. Currently using sample X_Ray image (shown below)""")
    #st.subheader("""[Awaiting X_ray image to be uploaded. Currently using sample X_Ray image (shown below)]""")
    c6.image(input_image)
    
class LeNet_for_1channel(nn.Module):
  def __init__(self):
    super(LeNet_for_1channel,self).__init__()
    self.cnn_model = nn.Sequential(
        nn.Conv2d(1,6,5,padding=(1,1),stride=(4,4)), # (40,1,244,244)-->(40,6,60,60)
        nn.Tanh(),
        nn.AvgPool2d(2,stride=2), # (40,6,60,60) --> (20,6,30,30)
        nn.Conv2d(6,16,3,padding=(1,1),stride=(2,2)), # (20,6,30,30) --> (20,16,14,14)
        nn.Tanh(),
        nn.AvgPool2d(2,stride=2) # (20,16,14,14) -->  (20,16,7,7) 
    )
    self.fc_model = nn.Sequential(
        nn.Linear(784,120),
        nn.Tanh(),
        nn.Linear(120,84),
        nn.Tanh(),
        nn.Linear(84,2),
        nn.Softmax()
    )
  def forward(self,x):
    x=self.cnn_model(x)
    x=x.view(x.size(0),-1)
    x=self.fc_model(x)
    return x
import monai
from monai.networks.nets import densenet121
model = densenet121(spatial_dims=2, in_channels=1,out_channels=2)#.to(device)#spatial_dims=2, in_channels=1,out_channels=num_classes
model.eval()
#load_model= model()
#st.write(input_new.shape)
output = model.load_state_dict(torch.load("best_metric_model_400epochs.pth",map_location=torch.device('cpu')))
output=model(input_new)
#st.write(output)
#st.write(nn.Softmax()(output.data[0])[1])

malignant_probability=nn.Softmax()(output.data[0])[1].cpu().numpy()

#malignant_probability2=torch.transpose(nn.Softmax()(output.data), 0,1)[1].cpu().numpy()
st.subheader('Predicted Malignant Probability')
st.write(np.around(malignant_probability*100,2),'%')

st.markdown("""<style>h1{color: #F9FF33;}</style>""", unsafe_allow_html=True)
st.markdown("""<style>h2{color: orange;}</style>""", unsafe_allow_html=True)
st.markdown("""<style>h3{color: #08FC58;}</style>""", unsafe_allow_html=True)
st.markdown("""<style>p{color: white;}</style>""", unsafe_allow_html=True)
st.markdown("""<style>h4{color: white;}</style>""", unsafe_allow_html=True)
