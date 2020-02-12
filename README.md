# QuestionRewrite

A Swagger UI/web service interface for the Question Rewrite service.

A service that accepts a properly formatted Robokop-like question and returns similar questions to the user.

## Deployment

Please download and implement the Docker container located in the Docker hub repo: renciorg\qrw. 

Kubernetes deployment files are available in the \kubernetes directory.

### Local environment

Note: This environment expects Python version 3.8.

Install required packages: pip install -r requirements.txt

Run: main.py

### Docker

```bash
cd <code base>
docker-compose build
docker-compose up -d
```
## Usage

<http://<hostname or IP>:6380/apidocs>
