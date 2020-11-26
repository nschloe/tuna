import pstats


def read_runtime_profile(prof_filename):
    stats = pstats.Stats(prof_filename)

    # One way of picking the root nodes would be to search through stats.stats.items()
    # and check which don't have parents. This, however, doesn't work if there are loops
    # in the graph which happens, for example, if exec() is called somewhere in the
    # program. For this reason, find all nodes without parents _and_ simply hardcode
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
            c.append(
                {
                    "text": [name + "::self", f"{selftime:.3} s"],
                    "color": 0,
                    "value": selftime,
                }
            )
            out = {"text": [name], "color": 0, "children": c}
        else:
            # More than one parent; we cannot further determine the call times.
            # Terminate the tree here.
            if children[key]:
                c = [
                    {
                        "text": [
                            "Possible calls of",
                            ", ".join(
                                "{}::{}::{}".format(*child) for child in children[key]
                            ),
                        ],
                        "color": 3,
                        "value": cumtime,
                    }
                ]
                out = {
                    "text": [name],
                    "color": 0,
                    "children": c,
                }
            else:
                out = {
                    "text": [name, f"{cumtime:.3f}"],
                    "color": 0,
                    "value": cumtime,
                }
        return out

    data = {
        "text": ["root"],
        "color": 0,
        "children": [populate(root, None) for root in roots],
    }
    return data
