import subprocess
import tempfile
import time
from pathlib import Path

import tuna  # noqa


def test_tuna():
    this_dir = Path(__file__).resolve().parent
    filename = this_dir / "foo.prof"
    cmd = ["tuna", filename, "--no-browser"]

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    # give server time to start up
    time.sleep(3)
    p.terminate()
    return


def test_importprofile():
    content = """
import time:       3 |    22 |     c
import time:       2 |    15 |   b
import time:       1 |    12 | a
"""

    ref = {
        "name": "main",
        "color": 0,
        "children": [
            {
                "name": "a",
                "value": 1e-06,
                "color": 0,
                "children": [
                    {
                        "name": "b",
                        "value": 2e-06,
                        "color": 0,
                        "children": [{"name": "c", "value": 3e-06, "color": 0}],
                    }
                ],
            }
        ],
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        filepath = Path(temp_dir) / "test.log"
        with open(filepath, "w") as f:
            f.write(content)

        out = tuna.read_import_profile(filepath)

    assert out == ref, ref


def test_importprofile_multiprocessing():
    # when using multiprocessing, you can have seemingly excessive indentation,
    # see <https://github.com/nschloe/tuna/issues/53>
    content = """
import time:       5 |    22 |       e
import time:       4 |    22 |   d
import time:       3 |    22 |     c
import time:       2 |    15 |   b
import time:       1 |    12 | a
"""
    ref = {
        "name": "main",
        "color": 0,
        "children": [
            {
                "name": "a",
                "value": 1e-06,
                "children": [
                    {
                        "name": "b",
                        "value": 2e-06,
                        "children": [
                            {
                                "name": "c",
                                "value": 3e-06,
                                "children": [
                                    {
                                        "name": "e",
                                        "value": 4.9999999999999996e-06,
                                        "color": 0,
                                    }
                                ],
                                "color": 0,
                            }
                        ],
                        "color": 0,
                    },
                    {"name": "d", "value": 4e-06, "color": 0},
                ],
                "color": 0,
            }
        ],
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        filepath = Path(temp_dir) / "test.log"
        with open(filepath, "w") as f:
            f.write(content)

        out = tuna.read_import_profile(filepath)

    assert out == ref, ref


if __name__ == "__main__":
    test_tuna()
