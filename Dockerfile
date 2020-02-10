FROM scratch

# update the container
RUN apt-get update

RUN mkdir /code
WORKDIR /code

RUN git clone https://github.com/TranslatorIIPrototypes/QuestionRewrite.git

RUN git checkout Phil_QRW

WORKDIR /code/QuestionRewrite

# install all required packages
RUN pip install -r requirements.txt

RUN pip install -e .

# start the service entry point
ENTRYPOINT ["main.py"]