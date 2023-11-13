# Prometheus File System Exporter

This exporter monitors file systems and S3 buckets, providing metrics for Prometheus.

## Features
- Monitor specific folders for the most recent file creation.
- Monitor folders for the most recent file creation matching a regex pattern.
- Monitor specific files for the last modification time.
- Monitor S3 buckets for the most recent file creation.

## Configuration
Edit `config.yaml` to set your monitoring paths and S3 buckets.

### Format
```yaml
folders:
  - /path/to/folder

regex_folders:
  - path: /path/to/regex/folder
    pattern: ".*\.log"

files:
  - /path/to/specific/file.txt

s3_buckets:
  - name: your-s3-bucket
    aws_access_key_id: your_access_key
    aws_secret_access_key: your_secret_key
