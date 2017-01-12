
def node_str_omit_none(node, *args):
    fields = ", ".join([": ".join([a[0], str(a[1])]) for a in args if a[1]])
    return "{clazz}({fields})".format(clazz=node.__class__.__name__, fields=fields)


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

FIELD_REFERENCE_PREFIX = "$field_reference$"


def mangle_field_reference(field_name):
    return FIELD_REFERENCE_PREFIX + field_name


def unmangle_field_reference(mangled_name):
    if not mangled_name.startswith(FIELD_REFERENCE_PREFIX):
        raise ValueError("Invalid mangled name: %s" % mangled_name)
    return mangled_name[len(FIELD_REFERENCE_PREFIX):]
