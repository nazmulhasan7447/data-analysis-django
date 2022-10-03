# this part for digital ocean static and media files
from storages.backends.s3boto3 import S3Boto3Storage

class MediaRootS3BotoStorage(S3Boto3Storage):
    location = "media"