import logging
import os
import pathlib
import tomllib as toml
from typing import Any

from globals import (
    REQUIRED_CONFIG_KEYS,
    REQUIRED_CONFIG_SUBKEYS,
)
from storage import (
    download_annotation_files_from_s3,
    get_local_annotation_files,
    init_s3_client,
    process_annotation_files,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _load_config() -> dict[str, Any]:
    with open("config.toml", "rb") as f:
        config = toml.load(f)

    logger.debug("Loaded configuration: %s", config.keys())

    for key in REQUIRED_CONFIG_KEYS:
        if key not in config:
            logger.error("Missing required configuration key: %s", key)
            raise ValueError(f"Missing required configuration key: {key}")

    for key, subkeys in REQUIRED_CONFIG_SUBKEYS.items():
        if key in config:
            for subkey in subkeys:
                if subkey not in config[key]:
                    logger.error(
                        "Missing required configuration subkey: %s.%s", key, subkey
                    )
                    raise ValueError(
                        f"Missing required configuration subkey: {key}.{subkey}"
                    )

    return config


if __name__ == "__main__":
    config = _load_config()
    s3_config = config["s3-connection"]

    s3_client, s3_paginator = init_s3_client(
        endpoint_url=s3_config["endpoint_url"],
        access_key=s3_config["access_key"],
        secret_key=s3_config["secret_key"],
    )

    target_folder = os.path.join(
        pathlib.Path(__file__).parent.absolute(),
        config["local-storage"]["label-exports"],
    )
    bucket_name = config["annotation-files"]["exoscale-bucket"]

    download_annotation_files_from_s3(
        s3_client=s3_client,
        bucket_name=bucket_name,
        s3_paginator=s3_paginator,
        target_folder=target_folder,
    )

    annotation_files = get_local_annotation_files(target_folder)
    logger.info(f"Total annotation files found: {len(annotation_files)}")

    process_annotation_files(
        annotation_files=annotation_files,
        s3_client=s3_client,
        yolo_labels_folder=config["local-storage"]["yolo-labels"],
        yolo_images_folder=config["local-storage"]["yolo-images"],
    )
