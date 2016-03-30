
def node_str_omit_none(node, *args):
    fields = ", ".join([": ".join([a[0], a[1]]) for a in args if a[1]])
    return "{class}({fields})".format(node.__class__.__name__, fields)


def node_str(node, *args):
    fields = ", ".join([": ".join([a[0], a[1] or "None"]) for a in args])
    return "{class}({fields})".format(node.__class__.__name__, fields)


# def node_repr_omit_none(node, *args):
#     fields = ", ".join([": ".join([a[0], a[1]]) for a in args if a[1]])
#     return "{class}({fields})".format(node.__class__.__name__, fields)
#
#
# def node_repr(node, *args):
#     fields = ", ".join([": ".join([a[0], a[1] or "None"]) for a in args])
#     return "{class}({fields})".format(node.__class__.__name__, fields)
