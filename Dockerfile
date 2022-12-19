FROM python:3.9
MAINTAINER info@neurallabs.africa

RUN echo "STARTED CREATING THE IMAGE COINTAINER"
RUN mkdir -p NeuralSight_AI
RUN apt-get update && apt-get -y install sudo
RUN sudo apt install -y libgl1-mesa-glx
COPY requirements.txt requirements.txt
COPY . NeuralSight_AI

RUN pip3 install --no-cache-dir --upgrade  -r requirements.txt
WORKDIR /NeuralSight_AI/application/

RUN echo "the PWD is : ${pwd}"
RUN echo "STOPPED CREATING THE IMAGE COINTAINER"
RUN echo "Run sudo docker-compose up to run the image container"
RUN pip3 uninstall jwt
RUN pip3 uninstall PyJWT
RUN pip3 install PyJWT
RUN python3 db_starter.py
RUN alembic upgrade 40aa33cd3fdb
RUN alembic upgrade e4ab6f930855
RUN alembic upgrade 0b6fef22e131
RUN python3 createsuperuser.py
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
