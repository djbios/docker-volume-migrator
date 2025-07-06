# Docker Volume Migrator

> Interactive command-line tool to copy Docker **named volumes** between two remote hosts over SSH – no local Docker daemon required.

## Features

* 📦 **Stream-based transfer** – data is piped directly between hosts, never written to disk
* 🔐 **SSH first** – authenticate with existing SSH keys/agents
* 🎛️ **Interactive wizard** – guided, step-by-step prompts to pick source/target hosts & volumes
* 🐳 **Minimal deps** – only needs Docker & `ssh` on your machine; the rest happens remotely
* 🪄 **One command** – install & run in seconds


## TODO (PRs welcome)
* Direct host to host transfer with ssh keys transfer
* Tests
* CLI options
* Non-interactive / automation
* Better overwrite control


## Installation

```bash
pip install docker-volume-migrator
```

or install the bleeding-edge version from GitHub:

```bash
pip install git+https://github.com/djbios/docker-volume-migrator.git
```

## Usage

```bash
docker-volume-migrate run
```

The wizard will:

1. Ask for the **source host** (SSH hostname/IP)
2. List its Docker volumes and let you pick which to copy
3. Ask for the **target host**
4. Let you create new destination volumes or map to existing ones
5. Show a summary and start the streaming transfer

### Non-interactive / automation

All prompts have sensible defaults and can be pre-answered by setting environment variables or using CLI options (coming soon).

## How it works

Under the hood, data is transferred via a TAR streaming pipeline:

```text
ssh SRC_HOST "docker run --rm -v SRC_VOL:/from alpine tar czf - -C /from ." \
  | ssh DST_HOST "docker run --rm -i -v DST_VOL:/to alpine tar xzf - -C /to"
```

No temporary files, no Docker daemon on your workstation.

## Contributing

Pull requests welcome! Please open an issue first to discuss major changes.

```bash
# set up dev env
git clone https://github.com/djbios/docker-volume-migrator.git
cd docker-volume-migrator
uv venv  # or python -m venv .venv
source .venv/bin/activate
uv pip install -e .[dev]
```

## License

[MIT](LICENSE)  © djbios
