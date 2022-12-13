FROM python:3.9
MAINTAINER info@neurallabs.africa

COPY requirements.txt requirements.txt
COPY ./application application

RUN pip3 install --no-cache-dir --upgrade  -r requirements.txt

WORKDIR /application/

echo "the PWD is : ${pwd}"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
