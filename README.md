# AutoML-DevOps 

Full-stack MLOps + DevOps pipeline that demonstrates automated model training, artifact management (S3), containerization, and CI/CD automation (Jenkins + Docker).
Note: I inspected your repository and created this README to match the repo structure I could see; some file contents were not accessible during inspection, so where necessary I explain expected behavior and give runnable examples you can paste into the repo. (See “Notes & assumptions” at the end.) 

# Table of contents

Project overview

High-level architecture

Repository structure

Prerequisites

Setup & run (local)

Docker workflow

Jenkins / CI pipeline

train-uploader module & upload_to_s3.py

Env variables / .env example

Extending the project / best practices

Troubleshooting

License & contact

Notes & assumptions (important)


# Project overview

AutoML-DevOps is a demonstration repo that integrates components commonly used in production DevOps/MLOps pipelines:

· Automates training workflows and uploads artifacts to cloud storage (S3).

· Builds reproducible environments using Docker.

· Provides CI/CD automation hooks (Jenkins) to run tests, build images and trigger training/deployment flows.

This README documents what each component does, how the pieces fit together, and how to run the project locally and in CI. 
GitHub

# High-level architecture

1. Source code & model code (Python) in the repository → stored in Git.

2. CI (Jenkins) triggers on push/PR → runs tests, creates build artifacts and Docker image.

3. Docker images are built and optionally pushed to a container registry.

4. Model training is handled by scripts in train-uploader/ which output model artifacts.

5. Artifact management: upload_to_s3.py pushes models and other artifacts to AWS S3 for versioning/storage.

6. (Optional) Orchestration or deployment layer consumes images/artifacts for inference.

**Flow:**

GitHub -> Jenkins -> (tests -> build) -> Docker image -> Registry
                           |
                           -> train-uploader -> model.pkl -> upload_to_s3 -> S3

**Repository structure**

Top-level items (as shown on GitHub): docker/, jenkins/, train-uploader/, .gitignore, README.md, upload_to_s3.py. Languages detected: Python, CSS, HTML, Dockerfile. 


Suggested descriptions (map to the repository):

1. docker/ — Dockerfiles and Docker build context for services (frontend/backend or training). Use this to build reproducible runtime images. 
GitHub

2. jenkins/ — Jenkins pipeline(s) / Jenkinsfile(s) or pipeline helper scripts to define CI/CD stages. Place the Jenkinsfile here or reference in Jenkins job configuration. 
GitHub

3. train-uploader/ — scripts and modules that run model training and prepare artifacts for upload (e.g., model serialization, metrics). 
GitHub

4. upload_to_s3.py — Python utility to upload files to AWS S3 (artifacts, models, logs). (See detailed usage below.) 
GitHub

**Prerequisites**

1. Git (clone repo)

2. Python 3.8+ and pip (or a virtualenv)

3. Docker & Docker CLI (for building images)

4. Jenkins server (if you want to run CI pipelines)

5. AWS CLI configured or AWS credentials (for S3 upload)

6. (Optional) Kubernetes cluster / kubectl if you plan to deploy images into k8s

**Setup & run (local)**

1. Clone

**git clone https://github.com/Safi-Ahmed-Shariff/AutoML-DevOps.git**
**cd AutoML-DevOps**


2. Create Python virtual environment & install (if requirements.txt exists)

**python -m venv .venv**
**source .venv/bin/activate**        # Linux / macOS
**.venv\Scripts\activate**           # Windows PowerShell

#If repo has requirements.txt:
**pip install -r requirements.txt**

#Otherwise install common deps (example)
**pip install boto3 scikit-learn pandas**


3. Run training script (example)
If train-uploader contains a script train.py, run:

**python train-uploader/train.py --config train-uploader/config.yml**


If a different entrypoint exists, call that script. See the train-uploader folder for actual filenames. 
GitHub

4. Upload an artifact

**python upload_to_s3.py --file path/to/model.pkl --bucket my-bucket --key models/model-v1.pkl**

(See upload_to_s3.py usage below for CLI flags and examples.) 
GitHub

**Docker workflow**

If the repo uses the docker/ directory as the build context:

1. Build

**docker build -t <dockerhub-username>/automl-devops:latest ./docker**


2. Run locally

**docker run --rm -p 5000:5000 <dockerhub-username>/automl-devops:latest**


3. Push to registry

**docker login**
**docker push <dockerhub-username>/automl-devops:latest**


Tip: Tag images with semantic versions (e.g., v0.1.0) and CI should automate image tagging based on build metadata or commit hash. 
GitHub

**Jenkins / CI pipeline**

The jenkins/ folder likely contains your pipeline config (Jenkinsfile or helpers). A recommended Declarative Jenkinsfile pipeline that fits this repo would:

1. checkout code

2. run unit tests (if any)

3. build Docker image

4. push image to registry (if configured)

5. run training script (optional stage)

6. run upload_to_s3.py to store artifacts

Example Jenkinsfile (drop into jenkins/Jenkinsfile or repo root):

pipeline {
  agent any
  environment {
    DOCKERHUB = credentials('dockerhub-credentials') // set on Jenkins
    AWS_ACCESS_KEY_ID = credentials('aws-access-key')
    AWS_SECRET_ACCESS_KEY = credentials('aws-secret-key')
  }
  stages {
    stage('Checkout') {
      steps { checkout scm }
    }
    stage('Unit tests') {
      steps {
        sh 'python -m pip install -r requirements.txt || true'
        sh 'pytest -q || true'
      }
    }
    stage('Build Docker') {
      steps {
        sh 'docker build -t $DOCKERHUB_USERNAME/automl-devops:${GIT_COMMIT:0:7} ./docker'
      }
    }
    stage('Push Image') {
      steps {
        sh 'docker push $DOCKERHUB_USERNAME/automl-devops:${GIT_COMMIT:0:7}'
      }
    }
    stage('Train & Upload') {
      steps {
        sh 'python train-uploader/train.py --output models/model.pkl'
        sh 'python upload_to_s3.py --file models/model.pkl --bucket my-bucket --key models/${GIT_COMMIT:0:7}.pkl'
      }
    }
  }
  post {
    success { echo 'Pipeline completed' }
    failure { mail to: 'you@example.com', subject: "Build failed", body: "Check Jenkins" }
  }
}


Adjust credentials, test commands and script names to match your actual files. 
GitHub

**train-uploader module & upload_to_s3.py**
**What train-uploader typically does**

1. Loads training data (local or S3).

2. Trains a model (for demo purposes could be a small scikit-learn pipeline).

3. Serializes the model (.pkl or .joblib).

4. Emits training metrics (accuracy, loss) to a metrics/ folder.

5. Calls or supports upload_to_s3.py to push artifacts.

Example run (replace filenames with actual ones from repo):

**python train-uploader/train.py --data data/train.csv --out models/model.pkl**

**upload_to_s3.py** (expected behavior & example)

This script uploads given file(s) to S3. Typical CLI usage:

**python upload_to_s3.py --file models/model.pkl --bucket my-bucket --key models/model-v1.pkl**


A minimal implementation (example) uses boto3:

# (example snippet - may differ from your file)
import boto3, argparse

def upload_file(file_path, bucket, key):
    s3 = boto3.client('s3')
    s3.upload_file(file_path, bucket, key)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True)
    parser.add_argument('--bucket', required=True)
    parser.add_argument('--key', required=True)
    args = parser.parse_args()
    upload_file(args.file, args.bucket, args.key)


If your upload_to_s3.py already exists, the example above shows expected behavior. Ensure boto3 is in requirements and AWS credentials are set in environment or AWS config. 
GitHub

**Environment variables / .env example**

Create a .env (or set env vars in CI):

# AWS
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...

# S3
S3_BUCKET=my-automl-bucket

# Database (if used)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_HOST=localhost
POSTGRES_DB=automl_db

# App secret (if needed)
SECRET_KEY=mysecret


Jenkins credentials should be used instead of plaintext in CI.

**Extending the project / best practices**

1. Model versioning: Add MLflow or DVC to track model versions and metrics.

2. Automated tests: Add unit tests for data preprocessing and model training to avoid regressions.

3. Security: Use Jenkins credentials store and IAM roles for production S3 access.

4. Deployment: Add a k8s/ manifest for inference deployment (Deployment + Service + HPA).

5. Observability: Add logging + metrics (Prometheus/Grafana or CloudWatch) for production deployments.

**Troubleshooting**

1. boto3 errors: ensure AWS keys are valid and bucket exists.

2. Docker permissions: add your user to the docker group or use sudo.

3. Jenkins build fails: check agent tooling (Python, Docker) installed on the Jenkins node.

4. If you get “file not found” for train-uploader scripts, confirm filenames in that directory (I could only see the folder listing). 
GitHub

**Contact**

📩 [Email me](mailto:safiahmedshariff@gmail.com?subject=AutoML-DevOps%20Project%20Query)
