yaml-serialize
==============

A simple wrapper around PyYAML to automatically serialize objects which are uniquely specified by their constructor arguments.

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
