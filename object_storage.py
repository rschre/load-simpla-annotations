import logging
import os

import boto3
from types_boto3_s3.client import S3Client
from types_boto3_s3.paginator import ListObjectsV2Paginator

logger = logging.getLogger(__name__)


def init_s3_client(
    endpoint_url: str, access_key: str, secret_key: str
) -> tuple[S3Client, ListObjectsV2Paginator]:
    s3_client = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    s3_paginator = s3_client.get_paginator("list_objects_v2")
    return s3_client, s3_paginator


def _get_folder_in_bucket(
    s3_paginator: ListObjectsV2Paginator, bucket_name: str
) -> list[str]:
    folders = []
    for page in s3_paginator.paginate(Bucket=bucket_name, Delimiter="/"):
        for obj in page.get("CommonPrefixes", []):
            folders.append(obj["Prefix"])
    return folders


def _get_annotation_files_from_s3(
    s3_paginator: ListObjectsV2Paginator, bucket_name: str, folder: str
) -> list[str]:
    annotation_files = []
    for page in s3_paginator.paginate(Bucket=bucket_name, Prefix=folder):
        for obj in page.get("Contents", []):
            if obj["Key"].endswith(".json"):
                annotation_files.append(obj["Key"])
    return annotation_files


def download_annotation_files_from_s3(
    s3_client: S3Client,
    bucket_name: str,
    s3_paginator: ListObjectsV2Paginator,
    target_folder: str,
) -> None:
    s3_folders = _get_folder_in_bucket(s3_paginator, bucket_name)
    for s3_folder in s3_folders:
        if not os.path.exists(os.path.join(target_folder, s3_folder)):
            os.makedirs(os.path.join(target_folder, s3_folder))

        logger.info(f"Processing folder: {s3_folder}")
        annotation_files = _get_annotation_files_from_s3(
            s3_paginator, bucket_name, s3_folder
        )
        for file in annotation_files:
            file_path = os.path.join(target_folder, s3_folder, file.split("/")[-1])
            s3_client.download_file(
                bucket_name,
                file,
                file_path,
            )
            logger.info(f"Downloaded {file} to {file_path}")
