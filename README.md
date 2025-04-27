# MultiSourceML_Project
Instructions to run this project are as below,<br />
1. Clone this Repository,<br />
$ git clone https://github.com/dshruti20/MultiSourceML_Project.git <br />
2. Run requirement.txt file to install the dependencies. It is important to have specified versions to run the files successfully. <br />
$ pip install -r requirements.txt <br />
3. To get the Memory Prediction and Job Completion Time for input model, run below command, <br />
$ python maincode.py -m resnet50 -b 64 -o inference -g 3080 <br />
Note: Possible Arguments for (-m : vgg11,vgg16,vgg19, resnet18, resnet50, resnet101, densenet121, densenet201), (-b : 16,32,34), (-o : trainingg, inference), (-g 2070s, 3080, 3090, 3070) . <br />
4. To test different ensemble learning models, <br />
$ cd cd Predictor Model Experiments  <br />
$ python ensemble_learning.py -m rfr <br />
Note: Possible Arguments for -m : rfr, gbr, abr, vr
