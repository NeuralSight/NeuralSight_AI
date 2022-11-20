# [NeuralSight Documentation](https://vlm0i2.sse.codesandbox.io/)

<img align="centre" src="https://github.com/NeuralSight/NeuralSight_AI/blob/main/images/Logo.jpg" width="712" height="512" />

NeuralSight AI is an intelligent tool that is capable of detection and highlighting pathologies on chest X-Ray images at runtime.

This repository contains the training code for our project entitled "NeuralSight Imaging AI".

You can find the project documentation [Here](https://vlm0i2.sse.codesandbox.io/)

## Abstract

On chest X-rays NeuralSight™ is capable of Identifying, Labeling and Highlighting over 20 respiratory diseases which include:
<br />

<img src="https://github.com/NeuralSight/NeuralSight_AI/blob/main/images/AI_Structure.png" width="712" height="256"/>

## Pipeline
### Model training
#### 1. Data Preparation:
* Image resize (640*640)
* Split data: training, testing, valid dataset(0.9, 0.1)
* Classes: Atelectasis, Infiltration, Emphysema, Mass, Nodule, Pleural Thickening, Effusion, Consolidation etc.


#### 2. Training Configuration
```
    Before starting training the script, an environment file (.env) will need to be created with the following parameters.
    
    DATA_DIRECTORY=<path to root folder of the data>
    TRAIN_DIR=<path to a directory where the training data and information will be placed>
    WANDB_API_KEY=<wandb secret key>
    CURR_DIR=<path to current working directory>
```
```
  step1: 
    pip install -r requirements.txt
  step2:
    python  cleaning.py
  step3:
    python process.py
  step4:
    python  extract.py
  step5:
    python -m training.py
  
```

#### 2. Running Inferences.
- `docker build -t <image name> .`
- `docker run -d -p 80:80 <image name>`
### Performance
**Table classification performance on the validation set.**
