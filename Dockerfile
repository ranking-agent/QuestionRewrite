FROM python:3.8.1-buster

# update the container
RUN apt-get update

RUN mkdir /repo
WORKDIR /repo

RUN git clone https://github.com/TranslatorIIPrototypes/QuestionRewrite.git

WORKDIR /repo/QuestionRewrite

# install all required packages
RUN pip install -r requirements.txt

RUN pip install -e .

# start the service entry point
ENTRYPOINT ["python3.8 main.py"]