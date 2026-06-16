import datetime as dt
import json
import logging
import os
import pathlib
from glob import glob

import boto3
import pandas as pd
from types_boto3_s3.client import S3Client
from types_boto3_s3.paginator import ListObjectsV2Paginator

from json_to_yolo import json_to_yolo

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
            if os.path.exists(file_path):
                logger.info(f"File already exists, skipping download: {file_path}")
                continue
            s3_client.download_file(
                bucket_name,
                file,
                file_path,
            )
            logger.info(f"Downloaded {file} to {file_path}")


logger = logging.getLogger(__name__)


def get_local_annotation_files(target_folder: str) -> list[str]:
    annotation_files = glob(os.path.join(target_folder, "**/*.json"), recursive=True)
    return annotation_files


def process_annotation_files(
    annotation_files: list[str],
    s3_client,
    yolo_labels_folder: str,
    yolo_images_folder: str,
) -> None:
    df_labels_dict = {}
    missing_files_log_path = os.path.join(
        pathlib.Path(__file__).parent.absolute(),
        f"{dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_failed_downloads.txt",
    )

    if not os.path.exists(yolo_labels_folder):
        os.makedirs(yolo_labels_folder)
    if not os.path.exists(yolo_images_folder):
        os.makedirs(yolo_images_folder)

    for file in annotation_files:
        logger.info(f"Processing annotation file: {file}")
        parent_folder = os.path.dirname(file)
        with open(file, "r") as f:
            labels = json.load(f)
        df_labels_dict[parent_folder] = pd.DataFrame(labels)
        json_to_yolo(file, yolo_labels_folder)

    for parent_folder, df_labels in df_labels_dict.items():
        for task in df_labels.itertuples():
            data = task.data  # type: ignore
            image_url = data.get("image")
            if image_url is None:
                logger.warning(f"No image URL found for data entry: {data}")
                continue
            image_path = pathlib.Path.joinpath(
                pathlib.Path(yolo_images_folder), image_url.split("/")[-1]
            )
            if not image_path.exists():
                try:
                    s3_client.download_file(
                        Bucket=parent_folder.split("/")[-1],
                        Key=image_url.split("/")[-1],
                        Filename=str(image_path),
                    )
                except Exception as e:
                    print(f"Failed to download {image_url}: {e}")
                    with open(
                        missing_files_log_path,
                        "a",
                    ) as log_file:
                        log_file.write(f"{image_url}\n")
