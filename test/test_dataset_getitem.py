##############################################################################
# Copyright by The HDF Group.                                                #
# All rights reserved.                                                       #
#                                                                            #
# This file is part of H5Serv (HDF5 REST Server) Service, Libraries and      #
# Utilities.  The full HDF5 REST Server copyright notice, including          #
# terms governing use, modification, and redistribution, is contained in     #
# the file COPYING, which can be found at the root of the source code        #
# distribution tree.  If you do not have access to this file, you may        #
# request a copy from help@hdfgroup.org.                                     #
##############################################################################
from __future__ import absolute_import
import logging
import numpy as np
import config

if config.get("use_h5py"):
    import h5py
else:
    import h5pyd as h5py

from common import ut, TestCase

"""
    Tests the h5py.Dataset.__getitem__ method.

    This module does not specifically test type conversion.  The "type" axis
    therefore only tests objects which interact with the slicing system in
    unreliable ways; for example, compound and array types.

    See test_dataset_getitem_types for type-conversion tests.

    Tests are organized into TestCases by dataset shape and type.  Test
    methods vary by slicing arg type.

    1. Dataset shape:
        Empty
        Scalar
        1D
        3D

    2. Type:
        Float
        Compound
        Array

    3. Slicing arg types:
        Ellipsis
        Empty tuple
        Regular slice
        Indexing
        Index list
        Boolean mask
        Field names
"""

"""
Disabled since low-level interface not supported with h5pyd
Update using new NULL dataset constructor once h5py 2.7 is out.
"""

class TestEmpty(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        filename = self.getFileName("dataset_testempty")
        print("filename:", filename)
        """
        self.f = h5py.File(filename, 'w')
        sid = h5py.h5s.create(h5py.h5s.NULL)
        tid = h5py.h5t.C_S1.copy()
        tid.set_size(10)
        dsid = h5py.h5d.create(self.f.id, b'x', tid, sid)
        self.dset = h5py.Dataset(dsid)
        """

    def test_ellipsis(self):
        """ Ellipsis -> IOError """
        pass
        """
        with self.assertRaises(IOError):
            out = self.dset[...]
        """

    def test_tuple(self):
        """ () -> IOError """
        pass
        """
        with self.assertRaises(IOError):
            out = self.dset[()]
        """

    def test_slice(self):
        """ slice -> ValueError """
        pass
        """
        with self.assertRaises(ValueError):
            self.dset[0:4]
        """

    def test_index(self):
        """ index -> ValueError """
        pass
        """
        with self.assertRaises(ValueError):
            self.dset[0]
        """

    def test_indexlist(self):
        """ index list -> ValueError """
        pass
        """
        with self.assertRaises(ValueError):
            self.dset[[1,2,5]]
        """

    def test_mask(self):
        """ mask -> ValueError """
        pass
        """
        mask = np.array(True, dtype='bool')
        with self.assertRaises(ValueError):
            self.dset[mask]
        """

    def test_fieldnames(self):
        """ field name -> ValueError """
        pass
        """
        with self.assertRaises(ValueError):
            self.dset['field']
        """
 
class TestScalarFloat(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        filename = self.getFileName("dataset_testscalarflot")
        print("filename:", filename)
        self.f = h5py.File(filename, 'w')
        if isinstance(self.f.id.id, str) and self.f.id.id.startswith("g-"):
            # flag if using HSDS
            self.is_hsds = True
        else:
            self.is_hsds = False
        self.data = np.array(42.5, dtype='f')
        self.dset = self.f.create_dataset('x', data=self.data)

    def test_ellipsis(self):
        """ Ellipsis -> scalar ndarray """
        out = self.dset[...]
        if not self.is_hsds:
            # TBD - fix for HSDS
            self.assertArrayEqual(out, self.data)

    def test_tuple(self):
        """ () -> bare item """
        out = self.dset[()]
        if not self.is_hsds:
            # TBD - fix for HSDS
            self.assertArrayEqual(out, self.data.item())

    def test_slice(self):
        """ slice -> ValueError """
        with self.assertRaises(ValueError):
            self.dset[0:4]

    def test_index(self):
        """ index -> ValueError """
        with self.assertRaises(ValueError):
            self.dset[0]

    # FIXME: NumPy has IndexError instead
    def test_indexlist(self):
        """ index list -> ValueError """
        with self.assertRaises(ValueError):
            self.dset[[1,2,5]]

    # FIXME: NumPy permits this
    def test_mask(self):
        """ mask -> ValueError """
        mask = np.array(True, dtype='bool')
        with self.assertRaises(ValueError):
            self.dset[mask]

    def test_fieldnames(self):
        """ field name -> ValueError (no fields) """
        with self.assertRaises(ValueError):
            self.dset['field']


class TestScalarCompound(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        filename = self.getFileName("dataset_testscalarcompound")
        print("filename:", filename)
        self.f = h5py.File(filename, 'w')
        if isinstance(self.f.id.id, str) and self.f.id.id.startswith("g-"):
            # array types not working with HSDS
            self.is_hsds = True
        else:
            self.is_hsds = False
        self.data = np.array((42.5, -118, "Hello"), dtype=[('a', 'f'), ('b', 'i'), ('c', '|S10')])
        #self.dset = self.f.create_dataset('x', data=self.data)
        self.dset = self.f.create_dataset('x', (), dtype=[('a', 'f'), ('b', 'i'), ('c', '|S10')])
        self.dset[...] =  (42.5, -118, "Hello")

    def test_ellipsis(self):
        """ Ellipsis -> scalar ndarray """
        out = self.dset[...]
        # assertArrayEqual doesn't work with compounds; do manually
        self.assertIsInstance(out, np.ndarray)
        if not self.is_hsds:
            # TBD: Fix for hsds
            self.assertEqual(out.shape, self.data.shape)
            self.assertEqual(out.dtype, self.data.dtype)

    def test_tuple(self):
        """ () -> np.void instance """
        out = self.dset[()]
        if not self.is_hsds:
            # TBD: Fix for HSDS
            self.assertIsInstance(out, np.void)
            self.assertEqual(out.dtype, self.data.dtype)

    def test_slice(self):
        """ slice -> ValueError """
        with self.assertRaises(ValueError):
            self.dset[0:4]

    def test_index(self):
        """ index -> ValueError """
        with self.assertRaises(ValueError):
            self.dset[0]

    # FIXME: NumPy has IndexError instead
    def test_indexlist(self):
        """ index list -> ValueError """
        with self.assertRaises(ValueError):
            self.dset[[1,2,5]]

    # FIXME: NumPy permits this
    def test_mask(self):
        """ mask -> ValueError  """
        mask = np.array(True, dtype='bool')
        with self.assertRaises(ValueError):
            self.dset[mask]

    # failed with earlier h5py versions
    def test_fieldnames(self):
        """ field name -> bare value """
        
        #TBD: fix when field access is supported in h5serv/hsds
        if config.get("use_h5py"):
            out = self.dset['a']
            self.assertIsInstance(out, np.float32)
            self.assertEqual(out, self.dset['a'])
         


class TestScalarArray(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        filename = self.getFileName("dataset_testscalararray")
        print("filename:", filename)
        self.f = h5py.File(filename, 'w')
        if isinstance(self.f.id.id, str) and self.f.id.id.startswith("g-"):
            # array types not working with HSDS
            self.is_hsds = True
        else:
            self.is_hsds = False
        self.dt = np.dtype('(3,2)f')
        self.data = np.array([(3.2, -119), (42, 99.8), (3.14, 0)], dtype='f')
        self.dset = self.f.create_dataset('x', (), dtype=self.dt)
        try:
            self.dset[...] = self.data
        except (IOError, OSError) as oe:
            #TBD" this is failing on HSDS
            if not self.is_hsds:
                raise oe

    # FIXME: HSDS failure
    def test_ellipsis(self):
        """ Ellipsis -> ndarray promoted to underlying shape """
        out = self.dset[...]
        if not self.is_hsds:
            self.assertArrayEqual(out, self.data)

    # FIXME: HSDS failure
    def test_tuple(self):
        """ () -> same as ellipsis """
        out = self.dset[...]
        if not self.is_hsds:
            self.assertArrayEqual(out, self.data)

    def test_slice(self):
        """ slice -> ValueError """
        with self.assertRaises(ValueError):
            self.dset[0:4]

    def test_index(self):
        """ index -> ValueError """
        with self.assertRaises(ValueError):
            self.dset[0]

    def test_indexlist(self):
        """ index list -> ValueError """
        with self.assertRaises(ValueError):
            self.dset[[]]

    def test_mask(self):
        """ mask -> ValueError """
        mask = np.array(True, dtype='bool')
        with self.assertRaises(ValueError):
            self.dset[mask]

    def test_fieldnames(self):
        """ field name -> ValueError (no fields) """
        with self.assertRaises(ValueError):
            self.dset['field']


class Test1DZeroFloat(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        filename = self.getFileName("dataset_test1dzerofloat")
        print("filename:", filename)
        self.f = h5py.File(filename, 'w')
        self.data = np.ones((0,), dtype='f')
        # TBD data in initializer not working
        #self.dset = self.f.create_dataset('x', data=self.data)
        self.dset = self.f.create_dataset('x', (0,), maxshape=(None,),  dtype='f')
        self.dset[...] = self.data

    def test_ellipsis(self):
        """ Ellipsis -> ndarray of matching shape """
        self.assertNumpyBehavior(self.dset, self.data, np.s_[...])

    def test_tuple(self):
        """ () -> same as ellipsis """
        self.assertNumpyBehavior(self.dset, self.data, np.s_[()])

    def test_slice(self):
        """ slice -> ndarray of shape (0,) """
        self.assertNumpyBehavior(self.dset, self.data, np.s_[0:4])

    # FIXME: NumPy raises IndexError
    def test_index(self):
        """ index -> out of range """
        with self.assertRaises(ValueError):
            self.dset[0]

    # FIXME: Under NumPy this works and returns a shape-(0,) array
    # Also, at the moment it rasies UnboundLocalError (!)
    @ut.expectedFailure
    def test_indexlist(self):
        """ index list """
        with self.assertRaises(ValueError):
            self.dset[[]]

    def test_mask(self):
        """ mask -> ndarray of matching shape """
        mask = np.ones((0,), dtype='bool')
        self.assertNumpyBehavior(self.dset, self.data, np.s_[mask])

    def test_fieldnames(self):
        """ field name -> ValueError (no fields) """
        with self.assertRaises(ValueError):
            self.dset['field']


class Test1DFloat(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        filename = self.getFileName("dataset_test1dfloat")
        print("filename:", filename)
        self.f = h5py.File(filename, 'w')
        self.data = np.arange(13).astype('f')
        # TBD data in initializer not working
        #self.dset = self.f.create_dataset('x', data=self.data)
        self.dset = self.f.create_dataset('x', (13,), dtype='f')
        self.dset[...] = self.data
        # self.dset = self.f.create_dataset('x', data=self.data)

    def test_ellipsis(self):
        self.assertNumpyBehavior(self.dset, self.data, np.s_[...])

    def test_tuple(self):
        self.assertNumpyBehavior(self.dset, self.data, np.s_[()])

    def test_slice_simple(self):
        self.assertNumpyBehavior(self.dset, self.data, np.s_[0:4])

    def test_slice_zerosize(self):
        self.assertNumpyBehavior(self.dset, self.data, np.s_[4:4])

    def test_slice_strides(self):
        self.assertNumpyBehavior(self.dset, self.data, np.s_[1:7:3])

    def test_slice_negindexes(self):
        self.assertNumpyBehavior(self.dset, self.data, np.s_[-8:-2:3])

    def test_slice_outofrange(self):
        self.assertNumpyBehavior(self.dset, self.data, np.s_[100:400:3])

    def test_slice_backwards(self):
        """ we disallow negative steps """
        with self.assertRaises(ValueError):
            self.dset[::-1]

    def test_slice_zerostride(self):
        self.assertNumpyBehavior(self.dset, self.data, np.s_[::0])

    def test_index_simple(self):
        self.assertNumpyBehavior(self.dset, self.data, np.s_[3])

    def test_index_neg(self):
        self.assertNumpyBehavior(self.dset, self.data, np.s_[-4])

    # FIXME: NumPy permits this... it adds a new axis in front
    def test_index_none(self):
        with self.assertRaises(TypeError):
            self.dset[None]

    # FIXME: NumPy raises IndexError
    # Also this currently raises UnboundLocalError. :(
    @ut.expectedFailure
    def test_index_illegal(self):
        """ Illegal slicing argument """
        with self.assertRaises(TypeError):
            self.dset[{}]

    # FIXME: NumPy raises IndexError
    def test_index_outofrange(self):
        with self.assertRaises(ValueError):
            self.dset[100]

    def test_indexlist_simple(self):
        self.assertNumpyBehavior(self.dset, self.data, np.s_[[1,2,5]])

    # Another UnboundLocalError
    #@ut.expectedFailure
    # Fails for h5py, but works for h5pyd
    def test_indexlist_empty(self):
        if not config.get('use_h5py'):
            self.assertNumpyBehavior(self.dset, self.data, np.s_[[]])
         

    # FIXME: NumPy has IndexError
    def test_indexlist_outofrange(self):
        with self.assertRaises(ValueError):
            self.dset[[100]]

    def test_indexlist_nonmonotonic(self):
        """ we require index list values to be strictly increasing """
        with self.assertRaises(TypeError):
            self.dset[[1,3,2]]

    # This results in IOError as the argument is not properly validated.
    # Suggest IndexError be raised.
    #@ut.expectedFailure  # works for h5pyd
    def test_indexlist_repeated(self):
        """ we forbid repeated index values """
        with self.assertRaises(TypeError):
            self.dset[[1,1,2]]

    def test_mask_true(self):
        self.assertNumpyBehavior(self.dset, self.data, np.s_[self.data > -100])

    def test_mask_false(self):
        self.assertNumpyBehavior(self.dset, self.data, np.s_[self.data > 100])

    def test_mask_partial(self):
        self.assertNumpyBehavior(self.dset, self.data, np.s_[self.data > 5])

    def test_mask_wrongsize(self):
        """ we require the boolean mask shape to match exactly """
        with self.assertRaises(TypeError):
            self.dset[np.ones((2,), dtype='bool')]

    def test_fieldnames(self):
        """ field name -> ValueError (no fields) """
        with self.assertRaises(ValueError):
            self.dset['field']


class Test2DZeroFloat(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        filename = self.getFileName("dataset_test2dzerofloat")
        print("filename:", filename)
        self.f = h5py.File(filename, 'w')
        self.data = np.ones((0,3), dtype='f')
        # TBD data in initializer not working
        self.dset = self.f.create_dataset('x', (0,3),  maxshape=(None,3), dtype='f')
        self.dset[...] = self.data
        #self.dset = self.f.create_dataset('x', data=self.data)

    @ut.expectedFailure
    def test_indexlist(self):
        """ see issue #473 """
        self.assertNumpyBehavior(self.dset, self.data, np.s_[:,[0,1,2]])

class Test3DFloat(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        filename = self.getFileName("dataset_test3dfloat")
        print("filename:", filename)
        self.f = h5py.File(filename, 'w')
        self.data = np.ones((4,6,8), dtype='f')
        # TBD data in initializer not working
        self.dset = self.f.create_dataset('x', (4,6,8), dtype='f')
        self.dset[...] = self.data
        #self.dset = self.f.create_dataset('x', data=self.data)

    def test_index_simple(self):
        self.assertNumpyBehavior(self.dset, self.data, np.s_[1,2:4,3:6])


if __name__ == '__main__':
    #loglevel = logging.DEBUG
    #logging.basicConfig(format='%(asctime)s %(message)s', level=loglevel)
    ut.main()
