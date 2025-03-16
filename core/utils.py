import boto3
from botocore.exceptions import ClientError
from core.settings import settings
from werkzeug.utils import secure_filename

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region,
)


def upload_file_to_s3(file, bucket: str, user_id: int) -> str:
    """Upload a file to S3 and return the public URL."""
    try:
        filename = secure_filename(file.filename)
        s3_key = f"avatars/{user_id}/{filename}"
        s3_client.upload_fileobj(
            file, bucket, s3_key, ExtraArgs={"ContentType": file.content_type}
        )
        return (
            f"https://{bucket}.s3.{settings.aws_region}.amazonaws.com/{s3_key}"
        )
    except ClientError as e:
        raise Exception(f"Failed to upload file to S3: {str(e)}")


def delete_file_from_s3(bucket: str, s3_key: str):
    """Delete a file from S3."""
    try:
        s3_client.delete_object(Bucket=bucket, Key=s3_key)
    except ClientError as e:
        raise Exception(f"Failed to delete file from S3: {str(e)}")
