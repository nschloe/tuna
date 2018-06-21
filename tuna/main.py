# -*- coding: utf-8 -*-
#
import json
import pstats


def read(filename):
    stats = pstats.Stats(filename)

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

    with open("test.json", "w") as f:
        json.dump(data, f, indent=2)
    return
