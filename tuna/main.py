# -*- coding: utf-8 -*-
#
import pstats


def read(filename):
    stats = pstats.Stats(filename)
    print(stats)
    return
