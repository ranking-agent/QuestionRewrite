LABEL maintainer="powen@renci.org"

# update the container
RUN apt-get update

# install all required packages
RUN pip install -r requirements.txt

# start the service entry point
ENTRYPOINT ["main.py"]