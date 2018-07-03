# -*- coding: utf-8 -*-
#
import os
import pstats
import threading
import webbrowser

import tornado.ioloop
import tornado.web

from .__about__ import __version__


def read(filename):
    _, ext = os.path.splitext(filename)
    if ext == ".prof":
        # runtime profile
        return read_runtime_profile(filename)

    return read_import_profile(filename)


def read_runtime_profile(prof_filename):
    stats = pstats.Stats(prof_filename)

    # One way of picking finding out the root notes would be to loop over
    # stats.stats.items() and check which doesn't have parents. This, however, doesn't
    # work if there are loops in the graph, occurring, for example, when exec() is
    # called somewhere in the program. For this reason, simple hardcode the root node.
    # This disregards the _lsprof.Profiler, but the runtime of this is typically so
    # small that it's okay to skip it.
    root = ("~", 0, "<built-in method builtins.exec>")

    # Collect children
    children = {key: [] for key in stats.stats.keys()}
    for key, value in stats.stats.items():
        _, _, _, _, parents = value
        for parent in parents:
            children[parent].append(key)

    def populate(key, parent):
        if parent is None:
            _, _, selftime, cumtime, parent_times = stats.stats[key]
            parent_times = []
        else:
            _, _, _, _, parent_times = stats.stats[key]
            _, _, selftime, cumtime = parent_times[parent]

        # Convert the tuple key into a string
        name = "{}::{}::{}".format(*key)
        if len(parent_times) <= 1:
            # Handle children
            # merge dictionaries
            c = [populate(child, key) for child in children[key]]
            c.append({"name": name + "::self", "value": selftime})
            out = {"name": name, "color": 0, "children": c}
        else:
            out = {"name": name, "color": 0, "value": cumtime}
        return out

    data = populate(root, None)

    return data


def read_import_profile(filename):
    # The import profile is of the form
    # ```
    # import time: self [us] | cumulative | imported package
    # import time:       378 |        378 | zipimport
    # import time:      1807 |       1807 | _frozen_importlib_external
    # import time:       241 |        241 |     _codecs
    # import time:      6743 |       6984 |   codecs
    # import time:      1601 |       1601 |   encodings.aliases
    # import time:     11988 |      20571 | encodings
    # import time:       700 |        700 | encodings.utf_8
    # import time:       535 |        535 | _signal
    # import time:      1159 |       1159 | encodings.latin_1
    # [...]
    # ```
    # The indentation in the last column signals parent-child relationships. In the
    # above example, `encodings` is parent to `encodings.aliases` and `codecs` which in
    # turn is parent to `_codecs`.
    entries = []
    with open(filename, "r") as f:
        line = f.readline()
        assert line == "import time: self [us] | cumulative | imported package\n"
        while True:
            line = f.readline()
            if not line:
                break  # EOF
            # remove `import time:`
            items = line[12:].strip().split("|")
            assert len(items) == 3
            self_time = int(items[0])
            last = items[2][1:]  # cut leading space
            name = items[2].lstrip()
            num_leading_spaces = len(last) - len(name)
            assert num_leading_spaces % 2 == 0
            level = num_leading_spaces // 2
            entries.append((name, level, self_time))

    # List taken from <https://docs.python.org/3/py-modindex.html>. Would be nice to get
    # it directly from code. <https://stackoverflow.com/q/8370206/353337>
    built_in = [
        "__future__",
        "__main__",
        "_dummy_thread",
        "_thread",
        "abc",
        "aifc",
        "argparse",
        "array",
        "ast",
        "asynchat",
        "asyncio",
        "asyncore",
        "atexit",
        "audioop",
        "base64",
        "bdb",
        "binascii",
        "binhex",
        "bisect",
        "builtins",
        "bz2" "calendar",
        "cgi",
        "cgitb",
        "chunk",
        "cmath",
        "cmd",
        "code",
        "codecs",
        "codeop",
        "collections",
        "colorsys",
        "compileall",
        "concurrent",
        "configparser",
        "contextlib",
        "contextvars",
        "copy",
        "copyreg",
        "cProfile",
        "crypt",
        "csv",
        "ctypes",
        "curses",
        "dataclasses",
        "datetime",
        "dbm",
        "decimal",
        "difflib",
        "dis",
        "distutils",
        "doctest",
        "dummy_threading",
        "email",
        "encodings",
        "ensurepip",
        "enum",
        "errno",
        "faulthandler",
        "fcntl",
        "filecmp",
        "fileinput",
        "fnmatch",
        "fractions",
        "ftplib",
        "functools",
        "gc",
        "getopt",
        "getpass",
        "gettext",
        "glob",
        "grp",
        "gzip",
        "hashlib",
        "heapq",
        "hmac",
        "html",
        "http",
        "imaplib",
        "imghdr",
        "importlib",
        "inspect",
        "io",
        "ipaddress",
        "itertools",
        "json",
        "keyword",
        "lib2to3",
        "linecache",
        "locale",
        "logging",
        "lzma",
        "macpath",
        "mailbox",
        "mailcap",
        "marshal",
        "math",
        "mimetypes",
        "mmap",
        "modulefinder",
        "msilib",
        "msvcrt",
        "multiprocessing",
        "netrc",
        "nis",
        "nntplib",
        "numbers",
        "operator",
        "os",
        "ossaudiodev",
        "parser",
        "pathlib",
        "pdb",
        "pickle",
        "pickletools",
        "pipes",
        "pkgutil",
        "platform",
        "plistlib",
        "poplib",
        "posix",
        "pprint",
        "profile",
        "pstats",
        "pty",
        "pwd",
        "py_compile",
        "pyclbr",
        "pydoc",
        "queue",
        "quopri",
        "random",
        "re",
        "readline",
        "reprlib",
        "resource",
        "rlcompleter",
        "runpy",
        "sched",
        "secrets",
        "select",
        "selectors",
        "shelve",
        "shlex",
        "shutil",
        "signal",
        "site",
        "smtpd",
        "smtplib",
        "sndhdr",
        "socket",
        "socketserver",
        "spwd",
        "sqlite3",
        "ssl",
        "stat",
        "statistics",
        "string",
        "stringprep",
        "struct",
        "subprocess",
        "sunau",
        "symbol",
        "symtable",
        "sys",
        "sysconfig",
        "syslog",
        "tabnanny",
        "tarfile",
        "telnetlib",
        "tempfile",
        "termios",
        "test",
        "textwrap",
        "threading",
        "time",
        "timeit",
        "tkinter",
        "token",
        "tokenize",
        "trace",
        "traceback",
        "tracemalloc",
        "tty",
        "turtle",
        "turtledemo",
        "types",
        "typing",
        "unicodedata",
        "unittest",
        "urllib",
        "uu",
        "uuid",
        "venv",
        "warnings",
        "wave",
        "weakref",
        "webbrowser",
        "winreg",
        "winsound",
        "wsgiref",
        "xdrlib",
        "xml",
        "xmlrpc",
        "zipapp",
        "zipfile",
        "zipimport",
        "zlib",
    ]

    built_in_deprecated = ["formatter", "imp", "optparse"]

    def shelf(lst, k):
        reference_level = lst[k][1]
        out = []
        while k < len(lst):
            name, level, self_time = lst[k]
            if level == reference_level:
                module = name.split(".")[0]
                if module in built_in:
                    color = 1
                elif module in built_in_deprecated:
                    color = 2
                else:
                    color = 0
                out.append({"name": name, "value": self_time * 1.0e-6, "color": color})
                k += 1
            elif level < reference_level:
                return out, k
            else:
                assert level == reference_level + 1
                out[-1]["children"], k = shelf(lst, k)
        return out, k

    lst, k = shelf(entries[::-1], 0)
    assert k == len(entries)

    return {"name": "main", "color": 0, "children": lst}


def start_server(prof_filename, start_browser):
    data = read(prof_filename)
    this_dir = os.path.dirname(__file__)
    data = data

    class IndexHandler(tornado.web.RequestHandler):
        def get(self):
            self.render(
                os.path.join(this_dir, "web", "index.html"),
                data=tornado.escape.json_encode(data),
                version=__version__,
            )
            return

    app = tornado.web.Application(
        [(r"/", IndexHandler)], static_path=os.path.join(this_dir, "web", "static")
    )

    port = None
    for prt in range(8000, 8100):
        try:
            app.listen(prt)
        except OSError:
            pass
        else:
            port = prt
            break
    assert port is not None, "Could not find open port."

    address = "http://localhost:{}".format(port)
    print("Started tuna server at {}".format(address))

    if start_browser:
        threading.Thread(target=lambda: webbrowser.open_new_tab(address)).start()

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()
        print("\nBye!")
    return
