import boto3
import botocore
from flask import app


def list_files_in_folder(bucket_name, folder_prefix):

    s3 = boto3.client(
        service_name="s3",
        aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
        endpoint_url=app.config['S3_URI']
    )

    try:
        response = s3.list_objects(Bucket=bucket_name, Prefix=folder_prefix)
        if 'Contents' in response:
            return [obj['Key'] for obj in response['Contents']]

        return []

    except botocore.exceptions.ClientError as e:
        print(f"Error listing files in the folder: {e}")
        return []
