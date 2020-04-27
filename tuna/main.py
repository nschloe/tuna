import html
import json
import logging
import mimetypes
import pstats
import socket
import string
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from .__about__ import __version__
from .module_groups import built_in, built_in_deprecated


class TunaError(Exception):
    pass


def read(filename):
    try:
        return read_import_profile(filename)
    except (TunaError, StopIteration):
        pass

    # runtime profile
    data = read_runtime_profile(filename)
    return data


def read_runtime_profile(prof_filename):
    stats = pstats.Stats(prof_filename)

    # One way of picking the root nodes would be to loop over stats.stats.items() and
    # check which doesn't have parents. This, however, doesn't work if there are loops
    # in the graph which happens, for example, if exec() is called somewhere in the
    # program. For this reason, find all nodes without parents and simply hardcode
    # `<built-in method builtins.exec>`.
    roots = set()
    for item in stats.stats.items():
        key, value = item
        if value[4] == {}:
            roots.add(key)

    default_roots = [
        ("~", 0, "<built-in method builtins.exec>"),
        ("~", 0, "<built-in method exec>"),
    ]
    for default_root in default_roots:
        if default_root in stats.stats:
            roots.add(default_root)
    roots = list(roots)

    # Collect children
    children = {key: [] for key in stats.stats.keys()}
    for key, value in stats.stats.items():
        _, _, _, _, parents = value
        for parent in parents:
            children[parent].append(key)

    def populate(key, parent):
        if parent is None:
            _, _, selftime, cumtime, _ = stats.stats[key]
            parent_times = {}
        else:
            _, _, x, _, parent_times = stats.stats[key]
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
            # More than one parent; we cannot further determine the call times.
            # Terminate the tree here.
            if children[key]:
                msg = "Possible calls of " + ", ".join(
                    "{}::{}::{}".format(*child) for child in children[key]
                )
                c = [{"name": msg, "color": 3, "value": cumtime}]
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


def _sort_into_tree(lst):
    main = {"name": "main", "color": 0, "children": []}

    # keep a dictionary of the last entry of any given level
    last = {}
    last[0] = main

    for entry in lst:
        name, level, time = entry
        # find the last entry with level-1
        last[level - 1]["children"] += [
            {"name": name, "value": time * 1.0e-6, "children": []}
        ]
        last[level] = last[level - 1]["children"][-1]

    _remove_empty_children(main)

    return [main]


def _remove_empty_children(tree):
    if not tree["children"]:
        del tree["children"]
    else:
        for k, child in enumerate(tree["children"]):
            tree["children"][k] = _remove_empty_children(child)
    return tree


def _add_color(tree, ancestor_is_built_in):
    for item in tree:
        module_name = item["name"].split(".")[0]
        is_built_in = (
            ancestor_is_built_in
            or module_name in built_in
            or module_name in built_in_deprecated
        )
        color = 1 if is_built_in else 0
        if module_name in built_in_deprecated:
            color = 2
        item["color"] = color
        if "children" in item:
            _add_color(item["children"], is_built_in)


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
    with open(filename) as f:
        # filtered iterator over lines prefixed with "import time: "
        try:
            line = next(f)
        except UnicodeError:
            raise TunaError()

        for line in f:
            if not line.startswith("import time: "):
                logging.warning(f"Didn't recognize and skipped line `{line.rstrip()}`")
                continue

            line = line[len("import time: ") :].rstrip()

            if line == "self [us] | cumulative | imported package":
                continue
            items = line.split(" | ")
            assert len(items) == 3
            self_time = int(items[0])
            last = items[2]
            name = last.lstrip()
            num_leading_spaces = len(last) - len(name)
            assert num_leading_spaces % 2 == 0
            indentation_level = num_leading_spaces // 2 + 1
            entries.append((name, indentation_level, self_time))

    tree = _sort_into_tree(entries[::-1])

    # go through the tree and add "color"
    _add_color(tree, False)

    return tree[0]


def render(data, prof_filename):
    this_dir = Path(__file__).resolve().parent
    with open(this_dir / "web" / "index.html") as _file:
        template = string.Template(_file.read())

    return template.substitute(
        data=html.escape(json.dumps(data).replace("</", "<\\/")),
        version=html.escape(__version__),
        filename=html.escape(prof_filename.replace("</", "<\\/")),
    )


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def start_server(prof_filename, start_browser, port):
    data = read(prof_filename)

    class StaticServer(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)

            if self.path == "/":
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(render(data, prof_filename).encode("utf-8"))
            else:
                this_dir = Path(__file__).resolve().parent
                filepath = this_dir / "web" / self.path[1:]

                mimetype, _ = mimetypes.guess_type(str(filepath))
                self.send_header("Content-type", mimetype)
                self.end_headers()

                with open(filepath, "rb") as fh:
                    content = fh.read()
                self.wfile.write(content)

            return

    if port is None:
        port = 8000
        while is_port_in_use(port):
            port += 1

    httpd = HTTPServer(("", port), StaticServer)

    if start_browser:
        address = f"http://localhost:{port}"
        threading.Thread(target=lambda: webbrowser.open_new_tab(address)).start()

    print(f"Starting httpd on port {port}")
    httpd.serve_forever()
