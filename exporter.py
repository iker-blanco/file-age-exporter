import os
import re
import time
import boto3
import yaml
from datetime import datetime
from prometheus_client import start_http_server, Gauge
from botocore.exceptions import NoCredentialsError


def get_time_since_last_matched_file(folder_path: str, pattern: str) -> float:
    try:
        regex = re.compile(pattern)
        matched_files = [f for f in os.listdir(folder_path) if regex.match(f)]
        if not matched_files:
            return -1
        most_recent = max([os.path.join(folder_path, f) for f in matched_files], key=os.path.getctime)
        return (time.time() - os.path.getctime(most_recent)) / 60
    except ValueError:
        return -1

def get_time_since_file_modified(file_path: str) -> float:
    if not os.path.isfile(file_path):
        return -1
    return (time.time() - os.path.getmtime(file_path)) / 60


# Function to get the time elapsed since the last file was created in a folder
def get_time_since_last_file_in_folder(folder_path: str) -> float:
    """Return time in minutes since the last file was created in the specified folder."""
    try:
        most_recent = max([os.path.join(folder_path, f) for f in os.listdir(folder_path)], key=os.path.getctime)
        elapsed_time = (time.time() - os.path.getctime(most_recent)) / 60
        return elapsed_time
    except ValueError:
        # No files in the folder
        return -1

# Function to get the time elapsed since the last file was created in an S3 bucket
def get_time_since_last_file_in_s3(bucket_name: str, aws_access_key_id: str, aws_secret_access_key: str) -> float:
    """Return time in minutes since the last file was created in the specified S3 bucket."""
    try:
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        objs = s3.list_objects_v2(Bucket=bucket_name)['Contents']
        last_added = max(objs, key=lambda x: x['LastModified'])
        elapsed_time = (datetime.now(last_added['LastModified'].tzinfo) - last_added['LastModified']).total_seconds() / 60
        return elapsed_time
    except (NoCredentialsError, KeyError):
        # Issue with credentials or no files in the bucket
        return -1

# Load configurations from YAML
def load_config(file_path: str) -> dict:
    """Load configuration from a YAML file."""
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

# Main function to setup Prometheus metrics
def main(config_path: str):
    # Load configuration
    config = load_config(config_path)

    # Prometheus metrics setup
    folder_metric = Gauge('folder_last_file_creation_time_minutes', 'Time since last file was created in folder', ['folder_path'])
    regex_metric = Gauge('folder_last_matched_file_creation_time_minutes', 'Time since last matched file was created in folder', ['folder_path', 'pattern'])
    file_metric = Gauge('file_last_modified_time_minutes', 'Time since file was last modified', ['file_path'])
    s3_metric = Gauge('s3_last_file_creation_time_minutes', 'Time since last file was created in S3 bucket', ['bucket_name'])

    # Start Prometheus client
    start_http_server(8000)

    while True:
        # Update folder metrics
        if 'folders' in config:
            for folder in config['folders']:
                elapsed_time = get_time_since_last_file_in_folder(folder)
                folder_metric.labels(folder_path=folder).set(elapsed_time)

        # Update regex metrics
        if 'regex_folders' in config:
            for item in config['regex_folders']:
                elapsed_time = get_time_since_last_matched_file(item['path'], item['pattern'])
                regex_metric.labels(folder_path=item['path'], pattern=item['pattern']).set(elapsed_time)

        # Update file metrics
        if 'files' in config:
            for file in config['files']:
                elapsed_time = get_time_since_file_modified(file)
                file_metric.labels(file_path=file).set(elapsed_time)

        # Update S3 metrics
        if 's3_buckets' in config:
            for bucket in config['s3_buckets']:
                elapsed_time = get_time_since_last_file_in_s3(bucket['name'], bucket['aws_access_key_id'], bucket['aws_secret_access_key'])
                s3_metric.labels(bucket_name=bucket['name']).set(elapsed_time)

        time.sleep(60)

if __name__ == '__main__':
    main('config.yaml')
