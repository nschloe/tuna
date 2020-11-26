import logging

from ._helpers import TunaError
from .module_groups import built_in, built_in_deprecated


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
            # skip first line
            next(f)
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


def _add_color(tree, ancestor_is_built_in):
    for item in tree:
        module_name = item["text"][0].split(".")[0]
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


def _sort_into_tree(lst):
    main = {"text": ["main"], "color": 0, "children": []}

    # keep a dictionary of the last entry of any given level
    last = {}
    last[0] = main

    for entry in lst:
        name, level, time = entry
        # find the last entry with level-1
        last[level - 1]["children"] += [
            {"text": [name], "value": time * 1.0e-6, "children": []}
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
