import logging
import tomllib as toml
from pathlib import Path
from typing import Any

import yaml

from globals import (
    LABELS_MAPPING,
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


def _load_config(config_path: Path) -> dict[str, Any]:
    with config_path.open("rb") as f:
        config = toml.load(f)

    logger.debug("Loaded configuration: %s", config.keys())

    required_sections = set(REQUIRED_CONFIG_KEYS) | set(REQUIRED_CONFIG_SUBKEYS)
    for section in required_sections:
        if section not in config:
            logger.error("Missing required configuration key: %s", section)
            raise ValueError(f"Missing required configuration key: {section}")

    for section, subkeys in REQUIRED_CONFIG_SUBKEYS.items():
        for subkey in subkeys:
            if subkey not in config[section]:
                logger.error(
                    "Missing required configuration subkey: %s.%s", section, subkey
                )
                raise ValueError(
                    f"Missing required configuration subkey: {section}.{subkey}"
                )

    return config


def _resolve_local_path(base_dir: Path, configured_path: str) -> str:
    path = Path(configured_path)
    if path.is_absolute():
        return str(path)
    return str(base_dir / path)


def _write_data_yaml(data_yaml_path: str, images_folder: str) -> None:
    data = {
        "path": images_folder,
        "names": LABELS_MAPPING,
    }
    Path(data_yaml_path).parent.mkdir(parents=True, exist_ok=True)
    with open(data_yaml_path, "w") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)

    logger.info("Wrote YOLO data config to %s", data_yaml_path)


def run() -> None:
    base_dir = Path(__file__).resolve().parent
    config = _load_config(base_dir / "config.toml")
    s3_config = config["s3-connection"]
    local_storage = config["local-storage"]

    s3_client, s3_paginator = init_s3_client(
        endpoint_url=s3_config["endpoint_url"],
        access_key=s3_config["access_key"],
        secret_key=s3_config["secret_key"],
    )

    target_folder = _resolve_local_path(base_dir, local_storage["label-exports"])
    yolo_labels_folder = _resolve_local_path(base_dir, local_storage["yolo-labels"])
    yolo_images_folder = _resolve_local_path(base_dir, local_storage["yolo-images"])
    yolo_data_yaml = _resolve_local_path(base_dir, local_storage["yolo-data-yaml"])
    bucket_name = config["annotation-files"]["exoscale-bucket"]

    # download_annotation_files_from_s3(
    #     s3_client=s3_client,
    #     bucket_name=bucket_name,
    #     s3_paginator=s3_paginator,
    #     target_folder=target_folder,
    # )

    # annotation_files = get_local_annotation_files(target_folder)
    # logger.info(f"Total annotation files found: {len(annotation_files)}")

    # process_annotation_files(
    #     annotation_files=annotation_files,
    #     s3_client=s3_client,
    #     yolo_labels_folder=yolo_labels_folder,
    #     yolo_images_folder=yolo_images_folder,
    # )

    _write_data_yaml(yolo_data_yaml, yolo_images_folder)


def main() -> int:
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
