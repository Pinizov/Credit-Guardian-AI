import os
import boto3
from fastapi import UploadFile
from botocore.exceptions import ClientError
from datetime import datetime

S3_BUCKET = os.getenv('AWS_S3_BUCKET', 'credit-guardian-contracts')
S3_REGION = os.getenv('AWS_REGION', 'eu-central-1')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

s3_client = None

def init_s3():
    global s3_client
    if AWS_ACCESS_KEY and AWS_SECRET_KEY:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=S3_REGION
        )
    return s3_client is not None

def upload_contract_to_s3(file: UploadFile, creditor_name: str = "unknown") -> str:
    """Upload contract PDF to S3 and return URL"""
    if not s3_client:
        raise Exception("S3 not configured")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_name = creditor_name.replace(' ', '_').replace('/', '_')
    filename = f"contracts/{safe_name}/{timestamp}_{file.filename}"
    
    try:
        s3_client.upload_fileobj(
            file.file,
            S3_BUCKET,
            filename,
            ExtraArgs={'ContentType': file.content_type}
        )
        
        url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{filename}"
        return url
    except ClientError as e:
        raise Exception(f"S3 upload failed: {str(e)}")

def get_contract_from_s3(s3_key: str) -> bytes:
    """Download contract from S3"""
    if not s3_client:
        raise Exception("S3 not configured")
    
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
        return response['Body'].read()
    except ClientError as e:
        raise Exception(f"S3 download failed: {str(e)}")
