# hatch-timestamp-version

[![PyPI version](https://img.shields.io/pypi/v/hatch-timestamp-version.svg)](https://pypi.org/project/hatch-timestamp-version/)
[![Python versions](https://img.shields.io/pypi/pyversions/hatch-timestamp-version.svg?logo=python&logoColor=white)](https://pypi.org/project/hatch-timestamp-version/)
[![CI](https://github.com/viseshrp/hatch-timestamp-version/actions/workflows/main.yml/badge.svg)](https://github.com/viseshrp/hatch-timestamp-version/actions/workflows/main.yml)
[![Coverage](https://codecov.io/gh/viseshrp/hatch-timestamp-version/branch/main/graph/badge.svg)](https://codecov.io/gh/viseshrp/hatch-timestamp-version)
[![License: MIT](https://img.shields.io/github/license/viseshrp/hatch-timestamp-version)](https://github.com/viseshrp/hatch-timestamp-version/blob/main/LICENSE)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://black.readthedocs.io/en/stable/)
[![Lint: Ruff](https://img.shields.io/badge/lint-ruff-000000.svg)](https://docs.astral.sh/ruff/)
[![Typing: mypy](https://img.shields.io/badge/typing-checked-blue.svg)](https://mypy.readthedocs.io/en/stable/)

> A [hatch](https://hatch.pypa.io/) plugin that provides a custom version scheme using UTC timestamps for development versions.

## 🚀 Why this project exists

I have CI continuously deploy to 'Test PyPI' and I want packages to have the datetime as
dev versions.

Eg: ``reelname-1.0.1.dev20250503202530-py3-none-any.whl``

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
requires = ["hatchling", "hatch-vcs", "hatch-timestamp-version"]
build-backend = "hatchling.build"

[tool.hatch.version]
source = "vcs"
scheme = "timestamp-dev"
validate-bump = true
path = "your_pkg/_version.py"

[tool.hatch.version.raw-options]
local_scheme = "no-local-version"
version_scheme = "guess-next-dev"
```

## 🛠️ Features

* Uses datetime for the dev versions, when used with hatch-vcs

```bash
$ hatch version
# => reelname-1.0.3.dev20250524011230
```

## 🧾 Changelog

See [CHANGELOG.md](https://github.com/viseshrp/hatch-timestamp-version/blob/main/CHANGELOG.md)

## 🙏 Credits

* Inspired by [Simon Willison](https://github.com/simonw)'s work.

## 📄 License

MIT © [Visesh Prasad](https://github.com/viseshrp)
