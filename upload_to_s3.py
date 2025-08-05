import boto3
import os 

s3 = boto3.client('s3')

local_file = os.path.join('docker', 'model.pkl')

bucket_name = 'automl-model-devops-artifacts'

s3_key = 'models/model.pkl'

s3.upload_file(local_file, bucket_name, s3_key)

print(f"Uploaded {local_file} to s3://{bucket_name}/{s3_key}")
