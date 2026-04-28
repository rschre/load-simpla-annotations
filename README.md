# Load-Simpla-Annotations

Code to load the annotations and images from simpla-gruen exported in label-studio format.
Start with the examples directory to get an overview of what can be done.

## Setup

Install dependencies using [uv](https://github.com/astral-sh/uv):

```bash
uv sync
```

Copy `config.toml` and fill in your credentials (see [Configuration](#configuration) below), then run:

```bash
uv run main.py
```

## Configuration

The project is configured via a `config.toml` file in the repository root. The file is not committed to version control — create it based on the example below.

```toml
[s3-connection]
access_key = "YOUR_ACCESS_KEY"
secret_key = "YOUR_SECRET_KEY"
endpoint_url = "https://sos-ch-dk-2.exo.io"

[annotation-files]
exoscale-bucket = "your-bucket-name"

[local-storage]
label-exports = "data/label-exports"
yolo-labels = "data/yolo-format/labels"
yolo-images = "data/yolo-format/images"
```

### Keys

| Section | Key | Description |
|---|---|---|
| `s3-connection` | `access_key` | S3-compatible object storage access key |
| `s3-connection` | `secret_key` | S3-compatible object storage secret key |
| `s3-connection` | `endpoint_url` | S3 endpoint URL |
| `annotation-files` | `exoscale-bucket` | Name of the bucket containing the label exports |
| `local-storage` | `label-exports` | Local path to download raw label-studio JSON exports |
| `local-storage` | `yolo-labels` | Local path for converted YOLO label files |
| `local-storage` | `yolo-images` | Local path for downloaded images |

