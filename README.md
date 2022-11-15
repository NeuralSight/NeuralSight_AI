# NeuralSight_AI
<img align="centre" src="https://github.com/NeuralSight/NeuralSight_AI/blob/main/images/Logo.jpg" width="712" height="512" />

NeuralSight AI is an intelligent tool that is capable of detection and highlighting pathologies on chest X-Ray images at runtime.

This repository contains the training code for our project entitled "NeuralSight Imaging AI".

## Abstract

On chest X-rays NeuralSight™ is capable of Identifying, Labeling and Highlighting over 20 respiratory diseases which include:


## Pipeline
### Model training
#### 1. Data Preparation:
* Image resize (640*640)
* Split data: training, testing, valid dataset(0.9, 0.1)
* Classes: Atelectasis, Infiltration, Emphysema, Mass, Nodule, Pleural Thickening, Effusion, Consolidation etc.


#### 2. Training Configuration
>>
  step1: 
    pip install -r requirements.txt
  step2:
    python app.py

### Performance
Table classification performance on the validation set.
