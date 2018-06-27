# tuna

[![CircleCI](https://img.shields.io/circleci/project/github/nschloe/tuna/master.svg)](https://circleci.com/gh/nschloe/tuna)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![PyPi Version](https://img.shields.io/pypi/v/tuna.svg)](https://pypi.org/project/tuna)
[![GitHub stars](https://img.shields.io/github/stars/nschloe/tuna.svg?logo=github&label=Stars)](https://github.com/nschloe/tuna)

### Installation

tuna is [available from the Python Package
Index](https://pypi.org/project/tuna/), so simply type
```
pip install -U tuna
```
to install or upgrade.


### Testing

To run the tuna unit tests, check out this repository and type
```
pytest
```

### Distribution

To create a new release

1. bump the `__version__` number,

2. tag and upload to PyPi:
    ```
    make publish
    ```

### License

tuna is published under the [MIT license](https://en.wikipedia.org/wiki/MIT_License).
