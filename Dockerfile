FROM python:3.8.1-buster

# update the container
RUN apt-get update

# make a directory for the repo
RUN mkdir /repo

# go to the directory where we are going to upload the repo
WORKDIR /repo

# get the latest code
RUN git clone https://github.com/TranslatorIIPrototypes/QuestionRewrite.git

# go to the repo dir
WORKDIR /repo/QuestionRewrite

# install all required packages
RUN pip install -r requirements.txt

# start the service entry point
ENTRYPOINT ["python", "main.py"]
