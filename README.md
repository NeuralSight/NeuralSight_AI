# [NeuralSight AI Documentation](https://neuralsight.github.io/NeuralSight_Docs/)

<img align="centre" src="https://github.com/NeuralSight/NeuralSight_AI/blob/main/images/Logo.jpg" width="712" height="512" />

Welcome to the NeuralSight Medical Image Detection GitHub repository! This repository contains code and resources for using deep learning techniques to detect specific features in medical images. The goal of this project is to improve the accuracy and efficiency of medical image analysis, with potential applications in diagnostics and treatment planning.

NeuralSight AI is an intelligent tool that is capable of detection and highlighting pathologies on chest X-Ray images at runtime.

This repository contains the training code for our project entitled "NeuralSight Imaging AI".

You can find the project documentation online [Here](https://neuralsight.github.io/NeuralSight_Docs/) and it's github repository [Here](https://github.com/NeuralSight/NeuralSight_Docs)

## License
The code in this repository is licensed under the GPL 3.0 license. This license allows for free use, distribution, and modification of the code, with the requirement that any derivative works must also be released under the GPL 3.0 license. You can find the full text of the GPL 3.0 license at the following link: https://www.gnu.org/licenses/gpl-3.0.en.html and a summary of the license can be found here: https://www.gnu.org/licenses/quick-guide-gplv3.html.

Please note that while this code is open-sourced, any medical data used in this code should be used only with permission and under strict compliance with patient privacy laws and regulations.

## Important Resources:
1. [What is NeuralSight](https://github.com/NeuralSight/Get-to-Understand-NeuralSight-AI)
2. [NeuralSight Project Documentation](https://neuralsight.github.io/NeuralSight_Docs/)
3. [NeuralSight Frontend Repository](https://github.com/NeuralSight/NeuralSight_frontend)
4. [Company Charter](https://github.com/NeuralSight/NeuralSight_Docs)
5. [Have a new Feature or an Issue you want fixed?](https://github.com/NeuralSight/NeuralSight_AI/tree/main/.github/ISSUE_TEMPLATE)


## Getting Started
1. Clone the repository
2. Install the required dependencies
3. Download the dataset and place it in the appropriate folder
4. Run the code
5. Prerequisites

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
```
   cd NeuralSight_AI

- `sudo docker build -t <image name> .`
- `docker run -d -p 80:80 <image name>`


OR

  sudo docker-compose build
  sudo docker-compose up
```
### Performance
**Table classification performance on the validation set.**


## Known Bugs.
{There are no known bugs}

## Support and contact details
{Any issues, questions, ideas, concerns or contributions to the code are highly encouraged. Contacts: info@neurallabs.africa, paul.ndirangu@neurallabs.africa & tom.kinyanjui@neurallabs.africa}
