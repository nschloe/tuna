# -*- coding: utf-8 -*-
#
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import mimetypes
import os
import pstats
import string
import threading
import webbrowser

try:
    from html import escape
except ImportError:
    from cgi import escape

from .__about__ import __version__
from .module_groups import built_in, built_in_deprecated


class TunaError(Exception):
    pass


def read(filename):
    _, ext = os.path.splitext(filename)
    try:
        return read_import_profile(filename)
    except (TunaError, StopIteration):
        pass

    # runtime profile
    return read_runtime_profile(filename)


def read_runtime_profile(prof_filename):
    stats = pstats.Stats(prof_filename)

    # One way of picking finding out the root notes would be to loop over
    # stats.stats.items() and check which doesn't have parents. This, however, doesn't
    # work if there are loops in the graph which happens, for example, if exec() is
    # called somewhere in the program. For this reason, find all nodes without parents
    # and simply hardcode `<built-in method builtins.exec>`.
    roots = []
    for item in stats.stats.items():
        key, value = item
        if value[4] == {}:
            roots.append(key)
    default_root = ("~", 0, "<built-in method builtins.exec>")
    if default_root in stats.stats:
        roots += [default_root]

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
            c.append({"name": name + "::self", "color": 0, "value": selftime})
            out = {"name": name, "color": 0, "children": c}
        else:
            out = {"name": name, "color": 0, "value": cumtime}
        return out

    data = {
        "name": "root",
        "color": 0,
        "children": [populate(root, None) for root in roots],
    }
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
        # filtered iterator over lines prefixed with "import time: "
        import_lines = (
            line[len("import time: ") :].rstrip()
            for line in f
            if line.startswith("import time: ")
        )

        try:
            line = next(import_lines)
        except UnicodeError:
            raise TunaError()

        for line in import_lines:
            if line == "self [us] | cumulative | imported package":
                continue
            items = line.split(" | ")
            assert len(items) == 3
            self_time = int(items[0])
            last = items[2]
            name = last.lstrip()
            num_leading_spaces = len(last) - len(name)
            assert num_leading_spaces % 2 == 0
            level = num_leading_spaces // 2
            entries.append((name, level, self_time))

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


def render(data):
    this_dir = os.path.dirname(__file__)
    with open(os.path.join(this_dir, "web", "index.html")) as _file:
        template = string.Template(_file.read())

    return template.substitute(
        data=escape(json.dumps(data).replace("</", "<\\/")), version=escape(__version__)
    )


def start_server(prof_filename, start_browser):
    data = read(prof_filename)

    class StaticServer(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)

            if self.path == "/":
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(render(data).encode("utf-8"))
            else:
                this_dir = os.path.dirname(__file__)
                # Remove the leading slash in self.path
                filepath = os.path.join(this_dir, "web", self.path[1:])

                mimetype, _ = mimetypes.guess_type(filepath)
                self.send_header("Content-type", mimetype)
                self.end_headers()

                with open(filepath, "rb") as fh:
                    content = fh.read()
                self.wfile.write(content)

            return

    port = 8000
    httpd = HTTPServer(("", port), StaticServer)

    if start_browser:
        address = "http://localhost:{}".format(port)
        threading.Thread(target=lambda: webbrowser.open_new_tab(address)).start()

    print("Starting httpd on port {}".format(port))
    httpd.serve_forever()
    return
