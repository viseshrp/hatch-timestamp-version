# hatch-timestamp-version

[![PyPI version](https://img.shields.io/pypi/v/hatch-timestamp-version.svg)](https://pypi.org/project/hatch-timestamp-version/)
[![Python versions](https://img.shields.io/pypi/pyversions/hatch-timestamp-version.svg?logo=python&logoColor=white)](https://pypi.org/project/hatch-timestamp-version/)
[![CI](https://github.com/viseshrp/hatch-timestamp-version/actions/workflows/main.yml/badge.svg)](https://github.com/viseshrp/hatch-timestamp-version/actions/workflows/main.yml)
[![Coverage](https://codecov.io/gh/viseshrp/hatch-timestamp-version/branch/main/graph/badge.svg)](https://codecov.io/gh/viseshrp/hatch-timestamp-version)
[![License: MIT](https://img.shields.io/github/license/viseshrp/hatch-timestamp-version)](https://github.com/viseshrp/hatch-timestamp-version/blob/main/LICENSE)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://black.readthedocs.io/en/stable/)
[![Lint: Ruff](https://img.shields.io/badge/lint-ruff-000000.svg)](https://docs.astral.sh/ruff/)
[![Typing: mypy](https://img.shields.io/badge/typing-checked-blue.svg)](https://mypy.readthedocs.io/en/stable/)

> A [hatch](https://hatch.pypa.io/) plugin that provides a custom version scheme using UTC timestamps for
> development versions. It is based on top of [hatch-vcs](https://github.com/ofek/hatch-vcs).

## 🚀 Why this project exists

I have CI continuously deploy to 'Test PyPI' and I want packages to have the datetime as
dev versions.

Eg: ``reelname-2.0.4.dev20250526231209-py3-none-any.whl``

## 📐 Requirements

* Python >= 3.9

## 📦 Installation

```bash
pip install hatch-timestamp-version
```

## 🧪 Usage

In your ``pyproject.toml``:
```toml
[build-system]
requires = ["hatchling", "hatch-timestamp-version>=0.0.5"]
build-backend = "hatchling.build"

[tool.hatch.version]
path = "yourpkg/_version.py"
source = "vcs-dev-timestamp"  # enables this plugin
validate-bump = true

[tool.hatch.version.raw-options]
local_scheme = "no-local-version"
# the only available config option for this plugin
timestamp_format = "short"  # or "long" for full datetime or any strftime string like "%Y%m%d%H%M"
```

## 🛠️ Features

* Uses datetime for the dev versions, when used with hatch-vcs
* Supports three options for timestamp format:
  * `short` - `YYYYMMDD`
  * `long` - `YYYYMMDDHHMMSS` (default)
  * Custom strftime formats like `%Y%m%d%H%M`

```bash
$ hatch version
2.0.4.dev20250526231209
```

## 🧾 Changelog

See [CHANGELOG.md](https://github.com/viseshrp/hatch-timestamp-version/blob/main/CHANGELOG.md)

## 🙏 Credits

* Inspired by [Simon Willison](https://github.com/simonw)'s work.

## 📄 License

MIT © [Visesh Prasad](https://github.com/viseshrp)
