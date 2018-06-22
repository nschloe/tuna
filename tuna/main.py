# -*- coding: utf-8 -*-
#
# import SimpleHTTPServer
import http.server
import json
import os
import pstats
import socketserver
import tempfile
import threading
import webbrowser


def read(prof_filename):
    stats = pstats.Stats(prof_filename)

    # Same as stats.stats.
    # import marshal
    # with open(filename, 'rb') as f:
    #     stats = marshal.load(f)

    # Get a dictionary of direct descendants
    root_nodes = []
    children = {key: [] for key in stats.stats.keys()}
    for key, value in stats.stats.items():
        _, _, _, _, parents = value
        for parent in parents:
            children[parent].append(key)
        if not parents:
            root_nodes.append(key)

    def populate(keys, parent):
        out = {}
        for key in keys:
            if parent is None:
                _, _, selftime, cumtime, parent_times = stats.stats[key]
            else:
                _, _, _, _, parent_times = stats.stats[key]
                _, _, selftime, cumtime = parent_times[parent]

            # Convert the tuple key into a string
            strkey = "{}::{}::{}".format(*key)
            if len(parent_times) <= 1:
                # Handle children
                # merge dictionaries
                out[strkey] = populate(children[key], key)
                out[strkey]["selftime"] = selftime
            else:
                out[strkey] = cumtime
        return out

    data = populate(root_nodes, None)

    json_filename = tempfile.NamedTemporaryFile().name
    with open(json_filename, "w") as f:
        json.dump(data, f, indent=2)
    return json_filename


class ServerThread(threading.Thread):
    def __init__(self, web_dir, port):
        threading.Thread.__init__(self)
        self.web_dir = web_dir
        self.port = port
        return

    def run(self):
        os.chdir(self.web_dir)

        Handler = http.server.SimpleHTTPRequestHandler
        httpd = socketserver.TCPServer(("", self.port), Handler)
        print("serving at port", self.port)
        httpd.serve_forever()
        return


def start_server():
    web_dir = os.path.join(os.path.dirname(__file__), 'web')
    ServerThread(web_dir, 8000).start()
    webbrowser.open_new_tab("tuna.html")
    return
