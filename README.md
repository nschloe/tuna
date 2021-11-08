<p align="center">
  <a href="https://github.com/nschloe/tuna"><img alt="tuna" src="https://nschloe.github.io/tuna/logo-with-text.svg" width="50%"></a>
  <p align="center">Performance analysis for Python.</p>
</p>

[![PyPi Version](https://img.shields.io/pypi/v/tuna.svg?style=flat-square)](https://pypi.org/project/tuna)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/tuna.svg?style=flat-square)](https://pypi.org/pypi/tuna/)
[![GitHub stars](https://img.shields.io/github/stars/nschloe/tuna.svg?style=flat-square&logo=github&label=Stars&logoColor=white)](https://github.com/nschloe/tuna)
[![Downloads](https://pepy.tech/badge/tuna/month?style=flat-square)](https://pepy.tech/project/tuna)
<!--[![PyPi downloads](https://img.shields.io/pypi/dm/tuna.svg?style=flat-square)](https://pypistats.org/packages/tuna)-->

[![Discord](https://img.shields.io/static/v1?logo=discord&label=chat&message=on%20discord&color=7289da&style=flat-square)](https://discord.gg/hnTJ5MRX2Y)

[![gh-actions](https://img.shields.io/github/workflow/status/nschloe/tuna/ci?style=flat-square)](https://github.com/nschloe/tuna/actions?query=workflow%3Aci)
[![LGTM](https://img.shields.io/lgtm/grade/python/github/nschloe/tuna.svg?style=flat-square)](https://lgtm.com/projects/g/nschloe/tuna)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)
[![code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg?style=flat-square)](https://github.com/prettier/prettier)

tuna is a modern, lightweight Python profile viewer inspired by
[SnakeViz](https://github.com/jiffyclub/snakeviz). It handles runtime and import
profiles, has minimal dependencies, uses [d3](https://d3js.org/) and
[bootstrap](https://getbootstrap.com/), and avoids
[certain](https://github.com/jiffyclub/snakeviz/issues/111)
[errors](https://github.com/jiffyclub/snakeviz/issues/112) present in SnakeViz (see
below) and is faster, too.

Create a runtime profile with

```
python -mcProfile -o program.prof yourfile.py
```

or an [import
profile](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPROFILEIMPORTTIME)
with

```
python -X importtime yourfile.py 2> import.log
```

and show it with

```
tuna program.prof
```

![](https://nschloe.github.io/tuna/screencast.gif)

### Why tuna doesn't show the whole call tree

The whole timed call tree _cannot_ be retrieved from profile data. Python developers
made the decision to only store _parent data_ in profiles because it can be computed
with little overhead. To illustrate, consider the following program.

```python
import time


def a(t0, t1):
    c(t0)
    d(t1)


def b():
    a(1, 4)


def c(t):
    time.sleep(t)


def d(t):
    time.sleep(t)


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

tuna only displays the part of the timed call tree that can be deduced from the profile.
SnakeViz, on the other hand, tries to construct the entire call tree, but ends up
providing lots of _wrong_ timings.

| ![](https://nschloe.github.io/tuna/snakeviz-example-wrong.png) |           ![](https://nschloe.github.io/tuna/foo.png)           |
| :------------------------------------------------------------: | :-------------------------------------------------------------: |
|                  SnakeViz output. **Wrong.**                   | tuna output. Only shows what can be retrieved from the profile. |

### Installation

tuna is [available from the Python Package Index](https://pypi.org/project/tuna/), so
simply do

```
pip install tuna
```

to install.

### Testing

To run the tuna unit tests, check out this repository and type

```
pytest
```

### IPython magics

tuna includes a `tuna` line / cell magic which can be used as a drop-in replacement for
the `prun` magic. Simply run `%load_ext tuna` to load the magic and then call it like
`%tuna sleep(3)` or

```python
%%tuna
sleep(3)
```

`prun` is still used to do the actual profiling and then the results are displayed in
the notebook.

### Development

After forking and cloning the repository, make sure to run `make dep` to install
additional dependencies (bootstrap and d3) which aren't stored in the repo.

### License

This software is published under the [GPLv3 license](https://www.gnu.org/licenses/gpl-3.0.en.html).
