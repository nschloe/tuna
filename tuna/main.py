# -*- coding: utf-8 -*-
#
import asyncio
import os
import pstats
import threading
import time
import webbrowser

import tornado.ioloop
import tornado.web


def read(prof_filename):
    stats = pstats.Stats(prof_filename)

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
        out = []
        for key in keys:
            if parent is None:
                _, _, selftime, cumtime, parent_times = stats.stats[key]
            else:
                _, _, _, _, parent_times = stats.stats[key]
                _, _, selftime, cumtime = parent_times[parent]

            # Convert the tuple key into a string
            name = "{}::{}::{}".format(*key)
            if len(parent_times) <= 1:
                # Handle children
                # merge dictionaries
                out.append({"name": name, "children": populate(children[key], key)})
                out[-1]["children"].append({"name": name + "::self", "value": selftime})
            else:
                out.append({"name": name, "value": cumtime})
        return out

    data = populate(root_nodes, None)
    # TODO perhaps remove this?
    data = {"name": "root", "children": data}

    # import pprint
    # pprint.pprint(data)
    # exit(1)

    # json_filename = tempfile.NamedTemporaryFile().name
    # print(json_filename)
    # with open(json_filename, "w") as f:
    #     json.dump(data, f, indent=2)

    return data


class ServerThread(threading.Thread):
    def __init__(self, prof_filename):
        threading.Thread.__init__(self)
        self.data = read(prof_filename)
        self.port = 8000
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
                    os.path.join(this_dir, "web", 'index.html'),
                    data=tornado.escape.json_encode(data)
                )
                return

        app = tornado.web.Application(
            [(r"/", IndexHandler)],
            static_path=os.path.join(this_dir, "web", "static"),
        )
        app.listen(self.port)
        tornado.ioloop.IOLoop.current().start()
        return


def start_server(prof_filename):
    thread = ServerThread(prof_filename)
    thread.start()
    webbrowser.open_new_tab("http://localhost:{}".format(thread.port))
    return
