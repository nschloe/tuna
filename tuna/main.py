# -*- coding: utf-8 -*-
#
import asyncio
import os
import pstats
import time
import threading
import webbrowser

import tornado.ioloop
import tornado.web

from .__about__ import __version__


def read(prof_filename):
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
            out = {"name": name, "children": c}
        else:
            out = {"name": name, "value": cumtime}
        return out

    data = populate(root, None)

    return data


class ServerThread(threading.Thread):
    def __init__(self, prof_filename):
        threading.Thread.__init__(self)
        self.data = read(prof_filename)
        self.port = None
        return

    def run(self):
        # Create event loop in this thread; cf.
        # <https://github.com/tornadoweb/tornado/issues/2183#issuecomment-371001254>.
        # If not used, one sees the error message
        # ```
        # RuntimeError: There is no current event loop in thread 'Thread-1'.
        # ```
        asyncio.set_event_loop(asyncio.new_event_loop())

        this_dir = os.path.dirname(__file__)
        data = self.data

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

        self.port = None
        for port in range(8000, 8100):
            try:
                app.listen(port)
            except OSError:
                pass
            else:
                self.port = port
                break
        assert self.port is not None, "Could not find open port."

        tornado.ioloop.IOLoop.current().start()
        return


def start_server(prof_filename):
    thread = ServerThread(prof_filename)
    thread.start()
    while thread.port is None:
        time.sleep(0.01)
    webbrowser.open_new_tab("http://localhost:{}".format(thread.port))
    return
