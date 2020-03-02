[![Build Status](https://travis-ci.com/TranslatorIIPrototypes/QuestionRewrite.svg?branch=master)](https://travis-ci.com/TranslatorIIPrototypes/QuestionRewrite)

# Question Augmentation

A Swagger UI/web service interface for the Question augmentation service.

A service that accepts a properly formatted ReasonerStd question and returns similar augmented questions to the user.

## Installation
Note: This environment expects Python version 3.8.

Create a virtual environment and activate.
    
    python -m venv venv
    source venv/bin/activate

Install dependencies
    
    pip install -r requirements.txt    
    
Run web server.

    python main.py --host 0.0.0.0 --port 6380

### Docker

You may also download and implement the Docker container located in the Docker hub repo: renciorg\qrw. 

```bash
cd <code base>
docker-compose build
docker-compose up -d
```
#### Launch
    docker run -it \ 
        -p <port>:6380 \ 
        QuestionAugmentation 
        
#### Usage

http://"host name or IP":"port"/apidocs

### Kubernetes 
Deployment files for Kubernetes are available in the \kubernetes directory.
        



