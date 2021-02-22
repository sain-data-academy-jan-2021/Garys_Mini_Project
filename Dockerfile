FROM python:3.9

WORKDIR /usr/app

COPY . .

RUN pip3 install -r data/requirements.txt

EXPOSE 80

ENTRYPOINT [ "python3", "-m", "src.app" ]