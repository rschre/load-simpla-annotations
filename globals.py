REQUIRED_CONFIG_KEYS = ["s3-connection", "annotation-files"]

REQUIRED_CONFIG_SUBKEYS = {
    "s3-connection": ["endpoint_url", "access_key", "secret_key"],
    "annotation-files": ["exoscale-bucket"],
    "local-storage": ["label-exports", "yolo-labels", "yolo-images", "yolo-data-yaml"],
}

LABELS_MAPPING = {
    0: "Schnur",
    1: "Container",
    2: "Zigaretten",
    3: "Kaffeekapsel",
    4: "Papier",
    5: "Katzensand",
    6: "Plastiksack",
    7: "Lebensmittelverpackung",
    8: "Alubuechse",
    9: "BAW-Sack",
    10: "Glasflasche",
    11: "Karton",
    12: "Alufolie",
    13: "PET 0.5l",
    14: "Textilien",
    15: "Metalle",
    16: "Windel",
    17: "PET 1.5l",
    18: "Styropor/Dämmung",
    19: "Blumentopf",
    20: "Diverses",
    21: "Gummiband",
    22: "Wagon",
}
