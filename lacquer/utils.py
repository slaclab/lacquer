# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
