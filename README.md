# tuna

[![CircleCI](https://img.shields.io/circleci/project/github/nschloe/tuna/master.svg)](https://circleci.com/gh/nschloe/tuna)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![PyPi Version](https://img.shields.io/pypi/v/tuna.svg)](https://pypi.org/project/tuna)
[![GitHub stars](https://img.shields.io/github/stars/nschloe/tuna.svg?logo=github&label=Stars&logoColor=white)](https://github.com/nschloe/tuna)

tuna is a Python profile viewer inspired by the amazing
[SnakeViz](https://github.com/jiffyclub/snakeviz).

Create a runtime profile with
```
python -mcProfile -o program.prof yourfile.py
```
or an [import
profile](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPROFILEIMPORTTIME)
with
```
python -X importprofile yourfile.py 2> import.log
```
and show it with
```
tuna program.prof
```

![](https://nschloe.github.io/tuna/screencast.gif)


### But tuna doesn't show the whole call tree!

Right, and that's because the whole timed call tree _cannot_ be retrieved from profile
data. Python developers made the decision to only store _parent data_ in profiles
because it can be computed with little overhead.
To illustrate, consider the following program.
```python
import time


def a(t0, t1):
    c(t0)
    d(t1)
    return


def b():
    return a(1, 4)


def c(t):
    time.sleep(t)
    return


def d(t):
    time.sleep(t)
    return


if __name__ == "__main__":
    a(4, 1)
    b()
```
The root process (`__main__`) calls `a()` which spends 4 seconds in `c()` and 1 second
in `d()`. `__main__` also calls `b()` which calls `a()`, this time spending 1 second in
`c()` and 4 seconds in `d()`. The profile, however, will only store that `c()` spent a
total of 5 seconds when called from `a()`, and likewise `d()`. The information that the
program spent more time in `c()` when called in `root -> a() -> c()` than when called in
`root -> b() -> a() -> c()` is not present in the profile.

tuna only displays the part of the timed call tree that can be deduced from the profile:
![](https://nschloe.github.io/tuna/foo.png)

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
