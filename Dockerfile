FROM python:3.8.1-buster

# update the container
RUN apt-get update

RUN mkdir /repo
WORKDIR /repo

RUN git clone https://github.com/TranslatorIIPrototypes/QuestionRewrite.git

RUN git checkout Phil_QRW

WORKDIR /repo/QuestionRewrite

# install all required packages
RUN pip install -r requirements.txt

RUN pip install -e .

# start the service entry point
ENTRYPOINT ["main.py"]