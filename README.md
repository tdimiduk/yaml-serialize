yaml-serialize
==============

A simple wrapper around PyYAML to automatically serialize objects
which are uniquely specified by their constructor arguments.

A simple use example would be:

    from yaml_serialize import Serializable, save, load

    class Point(Serializable):
        def __init__(self, x, y, z):
            self.x = x
            self.y = y
            self.z = z

    p = Point(1, 2, 3)
    save('point.yaml', p)
    loaded = load('point.yaml')

And point.yaml will look like:

    !Point
    x: 1
    y: 2
    z: 3

Installation
------------

yaml-serialize is a simple file that is BSD licensed so that you can
just include it directly in your projects.

yaml-serialize depends only on PyYAML. If you have NumPy installed, it will
define some extra things to make output of numpy stuff a little prettier.

If you prefer, you can also put the yaml-serialize.py file somewhere on your
pythonpath for system wide use.

Testing
-------

yaml-serialize has a small test suite intended to be run with nose. Run:

    nosetests

at a console in the same directory as this README.
