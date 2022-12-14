FROM python:3.9
MAINTAINER info@neurallabs.africa
RUN -p mkdir NeuralSight_AI
COPY requirements.txt requirements.txt
COPY . NeuralSight_AI

RUN pip3 install --no-cache-dir --upgrade  -r requirements.txt

WORKDIR /NeuralSight_AI/application/

#echo "the PWD is : ${pwd}"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
