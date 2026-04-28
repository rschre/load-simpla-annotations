REQUIRED_CONFIG_KEYS = ["s3-connection", "annotation-files"]

REQUIRED_CONFIG_SUBKEYS = {
    "s3-connection": ["endpoint_url", "access_key", "secret_key"],
    "annotation-files": ["exoscale-bucket"],
    "local-storage": ["target-folder"],
}
