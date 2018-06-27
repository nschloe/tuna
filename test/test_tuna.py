# -*- coding: utf-8 -*-
#
import os
import subprocess
import time

import tuna  # noqa


def test_tuna():
    this_dir = os.path.dirname(__file__)
    filename = os.path.join(this_dir, "foo.prof")
    cmd = ["tuna", filename, "--no-browser"]

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    # give server time to start up
    time.sleep(3)
    p.terminate()
    return


if __name__ == "__main__":
    test_tuna()
