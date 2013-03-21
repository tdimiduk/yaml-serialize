# Copyright (c) 2013 Thomas G. Dimiduk
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:

#   Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#   Redistributions in bytecode form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
# OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
# TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.
"""
Root class for all of holopy.  This class provides serialization to and from
yaml text file for all holopy objects.

yaml files are structured text files designed to be easy for humans to
read and write but also easy for computers to read.  HoloPy uses them
to store information about experimental conditions and to describe
analysis procedures.

.. moduleauthor:: Tom Dimiduk <tdimiduk@physics.harvard.edu>
"""
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
import inspect
import numpy as np
import yaml

# Metaclass black magic to eliminate need for adding yaml_tag lines to classes
class SerializableMetaclass(yaml.YAMLObjectMetaclass):
    def __init__(cls, name, bases, kwds):
        super(SerializableMetaclass, cls).__init__(name, bases, kwds)
        # Replace the normal yaml constructor with one that uses the class name
        # as the yaml tag.
        cls.yaml_loader.add_constructor('!{0}'.format(cls.__name__), cls.from_yaml)
        cls.yaml_dumper.add_representer(cls, cls.to_yaml)


class Serializable:
    """Class implementing yaml serialization

    Provides machinery for serializing subclasses to and from yaml
    text files. By default it inspects a class's constructor to learn
    what to save, but you can override _dict to change what variables
    are saved, or from_yaml and to_yaml to completely control the serialization. '

    """
    __metaclass__ = SerializableMetaclass

    @property
    def _dict(self):
        dump_dict = OrderedDict()

        for var in inspect.getargspec(self.__init__).args[1:]:
            if getattr(self, var, None) is not None:
                item = getattr(self, var)
                if isinstance(item, np.ndarray) and item.ndim == 1:
                    item = list(item)
                dump_dict[var] = item

        return dump_dict

    @classmethod
    def to_yaml(cls, dumper, data):
        return ordered_dump(dumper, '!{0}'.format(data.__class__.__name__), data._dict)


    @classmethod
    def from_yaml(cls, loader, node):
        fields = loader.construct_mapping(node, deep=True)
        return cls(**fields)

    def __repr__(self):
        keywpairs = ["{0}={1}".format(k[0], repr(k[1])) for k in self._dict.iteritems()]
        return "{0}({1})".format(self.__class__.__name__, ", ".join(keywpairs))

    def __str__(self):
        return self.__repr__()


# ordered_dump code is heavily inspired by the source of PyYAML's represent_mapping
def ordered_dump(dumper, tag, data):
    value = []
    node = yaml.nodes.MappingNode(tag, value)
    for key, item in data.iteritems():
        node_key = dumper.represent_data(key)
        node_value = dumper.represent_data(item)
        value.append((node_key, node_value))

    return node


###################################################################
# Custom Yaml Representers
###################################################################
# These functions provide prettier representation of some numpy
# types.
###################################################################

def ignore_aliases(data):
    try:
        if data in [None, ()]:
            return True
        if isinstance(data, (str, unicode, bool, int, float)):
            return True
    except TypeError, e:
        pass
yaml.representer.SafeRepresenter.ignore_aliases = \
    staticmethod(ignore_aliases)

# Represent 1d ndarrays as lists in yaml files because it makes them much
# prettier
def ndarray_representer(dumper, data):
    return dumper.represent_list(data.tolist())
yaml.add_representer(np.ndarray, ndarray_representer)

# represent tuples as lists because yaml doesn't have tuples
def tuple_representer(dumper, data):
    return dumper.represent_list(list(data))
yaml.add_representer(tuple, tuple_representer)

# represent numpy types as things that will print more cleanly
def complex_representer(dumper, data):
    return dumper.represent_scalar('!complex', repr(data.tolist()))
yaml.add_representer(np.complex128, complex_representer)
def complex_constructor(loader, node):
    return complex(node.value)
yaml.add_constructor('!complex', complex_constructor)

def numpy_float_representer(dumper, data):
    return dumper.represent_float(float(data))
yaml.add_representer(np.float64, numpy_float_representer)

def numpy_int_representer(dumper, data):
    return dumper.represent_int(int(data))
yaml.add_representer(np.int64, numpy_int_representer)
yaml.add_representer(np.int32, numpy_int_representer)

def numpy_dtype_representer(dumper, data):
    return dumper.represent_scalar('!dtype', data.name)
yaml.add_representer(np.dtype, numpy_dtype_representer)

def numpy_dtype_loader(loader, node):
    name = loader.construct_scalar(node)
    return np.dtype(name)
yaml.add_constructor('!dtype', numpy_dtype_loader)
