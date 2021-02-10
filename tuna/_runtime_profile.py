import pstats


def read_runtime_profile(prof_filename):
    stats = pstats.Stats(prof_filename)

    # # stats.strip_dirs()
    # stats.sort_stats("cumulative")
    # # # stats.sort_stats("time")
    # stats.print_stats(10)
    # exit(1)
    # s = stats.get_stats_profile()
    # print(s)
    # exit(1)

    # One way of picking the root nodes would be to search through stats.stats.items()
    # and check which don't have parents. This, however, doesn't work if there are loops
    # in the graph which happens, for example, if exec() is called somewhere in the
    # program. For this reason, find all nodes without parents _and_ simply hardcode
    # `<built-in method builtins.exec>`.
    roots = set()
    for key, value in stats.stats.items():
        # The object {('~', 0, "<method 'disable' of '_lsprof.Profiler' objects>")}
        # is part of the profile and a root node. Its runtime is usually miniscule and
        # doesn't appear the the final output. Hence, only consider root nodes with a
        # cumtime larger than a threshold.
        # If there is only one remaining root (which is most often the case), one can
        # cut of the artificial "root" node. See below.
        if not value[4] and value[3] > 1.0e-5:
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

    def populate(key, parent, all_ancestors):
        # stats.stats[key] returns a tuple of length 5 with the following data:
        # [0]: total calls
        # [1]: prim calls
        # [2]: selftime
        # [3]: cumtime
        # [4]: a dictionary of callers
        if parent is None:
            parent_times = {}
            _, _, selftime, cumtime, _ = stats.stats[key]
        else:
            _, _, _, _, parent_times = stats.stats[key]
            _, _, selftime, cumtime = parent_times[parent]

        # Convert the tuple key into a string
        name = "{}::{}::{}".format(*key)

        if key in all_ancestors:
            # avoid loops
            return {}

        if len(parent_times) <= 1:
            # Handle children
            c = [populate(child, key, all_ancestors + [key]) for child in children[key]]
            c.append(
                {
                    "text": [name + "::self", f"{selftime:.3} s"],
                    "color": 0,
                    "value": selftime,
                }
            )
            return {"text": [name], "color": 0, "children": c}

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
            return {"text": [name], "color": 0, "children": c}

        return {"text": [name, f"{selftime:.3f}"], "color": 0, "value": selftime}

    if len(roots) == 1:
        data = populate(roots[0], None, [])
    else:
        # If there is more than one root, add an artificial "main root" item that is
        # parent to all roots.
        assert len(roots) > 1
        data = {
            "text": ["root"],
            "color": 0,
            "children": [populate(root, None, []) for root in roots],
        }
    return data
