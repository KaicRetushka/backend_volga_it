FROM ubuntu:latest

RUN apt update && apt install -y python3 python3-pip python3-venv

COPY . /app_1

WORKDIR /app_1

RUN python3 -m venv venv

RUN ./venv/bin/pip install -r requirements.txt

CMD [ "./venv/bin/python", "main_1.py"]