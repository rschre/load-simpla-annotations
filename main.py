import logging
import os
import pathlib
import tomllib as toml
from typing import Any

from globals import (
    REQUIRED_CONFIG_KEYS,
    REQUIRED_CONFIG_SUBKEYS,
)
from object_storage import download_annotation_files_from_s3, init_s3_client

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
        config["local-storage"]["target-folder"],
    )
    bucket_name = config["annotation-files"]["exoscale-bucket"]

    download_annotation_files_from_s3(
        s3_client=s3_client,
        bucket_name=bucket_name,
        s3_paginator=s3_paginator,
        target_folder=target_folder,
    )
