import os
import sys
# put the parent directory (where yaml_serialize lives) on the path to
# guarantee we can import it.
sys.path.append(os.path.split(os.path.split(os.path.abspath(__file__))[0])[0])
from yaml_serialize import Serializable, save, load
import yaml
from nose.plugins.skip import SkipTest
import tempfile
from nose.tools import assert_equal

def assert_read_matches_write(o):
    tempf = tempfile.NamedTemporaryFile()
    save(tempf, o)
    tempf.flush()
    tempf.seek(0)
    loaded = load(tempf)
    assert_obj_close(o, loaded)


def assert_obj_close(actual, desired, rtol=1e-7, atol = 0, context = 'tested_object'):
    try:
        import numpy as np
    except ImportError:
        pass
    # We try a bunch of different asserts to try to give the most
    # helpful error message, but eventually fall back to just
    # comparing objects to make sure nothing slips through.

    # we go ahead and try to compare anything using numpy's assert allclose, if
    # it fails it probably gives more useful error messages than later options,
    # and catching NotImplementedError and TypeError should cause this to
    # silently fall through for other types
    try:
        np.testing.assert_allclose(actual, desired, rtol = rtol, atol = atol, err_msg=context)
    except (NotImplementedError, TypeError, NameError):
        pass

    if isinstance(actual, dict) and isinstance(desired, dict):
        for key, val in actual.iteritems():
            assert_obj_close(actual[key], desired[key], context = '{0}[{1}]'.format(context, key),
                             rtol = rtol, atol = atol)
    elif hasattr(actual, '_dict') and hasattr(desired, '_dict'):
        assert_obj_close(actual._dict, desired._dict, rtol=rtol, atol=atol,
                         context = "{0}._dict".format(context))
    elif isinstance(actual, (list, tuple)):
        assert_equal(len(actual), len(desired), err_msg=context)
        for i, item in enumerate(actual):
            assert_obj_close(actual[i], desired[i], context = '{0}[{1}]'.format(context, i),
                             rtol = rtol, atol = atol)
    elif hasattr(actual, '__dict__'):
        assert_obj_close(actual.__dict__, desired.__dict__, rtol = rtol,
                         atol = atol, context = context + '.__dict__')
    else:
        try:
            np.testing.assert_allclose(actual, desired, rtol=rtol, atol=atol, err_msg=context)
        except (TypeError, NotImplementedError, NameError):
            assert_equal(actual, desired, err_msg=context)


# test a number of little prettying up of yaml output that we do for
# numpy types
def test_numpy_output():
    try:
        import numpy as np
    except ImportError:
        raise SkipTest
    # test that numpy types get cleaned up into python types for clean printing
    a = np.ones(10, 'int')

    assert_equal(yaml.dump(a), '[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]\n')
    assert_equal(yaml.dump(a.std()), '0.0\n...\n')

    assert_equal(yaml.dump(np.dtype('float')),"!dtype 'float64'\n")
    assert_equal(yaml.load(yaml.dump(np.dtype('float'))), np.dtype('float64'))

def test_32_bit_bug():
    # this should fail on Windows64 because int and long are both
    # int32
    try:
        import numpy as np
    except ImportError:
        raise SkipTest
    a = np.ones(10, 'int')
    try:
        assert_equal(yaml.dump(a. max()), '1\n...\n')
    except AssertionError as err:
        if err.args[0] == r"""
Items are not equal:
 ACTUAL: '!!python/object/apply:numpy.core.multiarray.scalar [!dtype \'int32\', "\\x01\\0\\0\\0"]\n'
 DESIRED: '1\n...\n'""":
            raise AssertionError("You're probably running a 32 bit OS.  Writing and reading files with integers migth be buggy on 32 bit OS's, we don't think it will lead to data loss, but we make no guarantees'. If you see this on 64 bit operating systems, please let us know by filing a bug.")
        else:
            raise err

def test_class():
    class Point(Serializable):
        def __init__(self, x, y, z):
            self.x = x
            self.y = y
            self.z = z

    p = Point(1, 2, 3)
    assert_read_matches_write(p)

    assert_equal(repr(p), 'Point(x=1, y=2, z=3)')
    assert_equal(str(p), 'Point(x=1, y=2, z=3)')

def test_tuple():
    t = (1, 3, 'bob')
    assert_equal(yaml.dump(t), '[1, 3, bob]\n')

def test_complex():
