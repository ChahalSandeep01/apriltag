#!/usr/bin/env python

"""Python wrapper for C version of apriltags. This program creates two
classes that are used to detect apriltags and extract information from
them. Using this module, you can identify all apriltags visible in an
image, and get information about the location and orientation of the
tags.

Original author: Isaac Dulin, Spring 2016
Updates: Matt Zucker, Fall 2016
Modifications; Sandeep Chahal

"""

import ctypes
import collections
import os
import re
import numpy

######################################################################

# pylint: disable=R0903

class _ImageU8(ctypes.Structure):
    '''Wraps image_u8 C struct.'''
    _fields_ = [
        ('width', ctypes.c_int),
        ('height', ctypes.c_int),
        ('stride', ctypes.c_int),
        ('buf', ctypes.POINTER(ctypes.c_uint8))
    ]

class _Matd(ctypes.Structure):
    '''Wraps matd C struct.'''
    _fields_ = [
        ('nrows', ctypes.c_int),
        ('ncols', ctypes.c_int),
        ('data', ctypes.c_double*1),
    ]

class _ZArray(ctypes.Structure):
    '''Wraps zarray C struct.'''
    _fields_ = [
        ('el_sz', ctypes.c_size_t),
        ('size', ctypes.c_int),
        ('alloc', ctypes.c_int),
        ('data', ctypes.c_void_p)
    ]

class _ApriltagFamily(ctypes.Structure):
    '''Wraps apriltag_family C struct.'''
    _fields_ = [
        ('ncodes', ctypes.c_int32),
        ('codes', ctypes.POINTER(ctypes.c_int64)),
        ('black_border', ctypes.c_int32),
        ('d', ctypes.c_int32),
        ('h', ctypes.c_int32),
        ('name', ctypes.c_char_p),
    ]

class _ApriltagDetection(ctypes.Structure):
    '''Wraps apriltag_detection C struct.'''
    _fields_ = [
        ('family', ctypes.POINTER(_ApriltagFamily)),
        ('id', ctypes.c_int),
        ('hamming', ctypes.c_int),
        ('goodness', ctypes.c_float),
        ('decision_margin', ctypes.c_float),
        ('H', ctypes.POINTER(_Matd)),
        ('c', ctypes.c_double*2),
        ('p', (ctypes.c_double*2)*4)
    ]

class _ApriltagDetector(ctypes.Structure):
    '''Wraps apriltag_detector C struct.'''
    _fields_ = [
        ('nthreads', ctypes.c_int),
        ('quad_decimate', ctypes.c_float),
        ('quad_sigma', ctypes.c_float),
        ('refine_edges', ctypes.c_int),
        ('refine_decode', ctypes.c_int),
        ('refine_pose', ctypes.c_int),
        ('debug', ctypes.c_int),
        ('quad_contours', ctypes.c_int),
    ]

######################################################################

def _ptr_to_array2d(datatype, ptr, rows, cols):
    array_type = (datatype*cols)*rows
    array_buf = array_type.from_address(ctypes.addressof(ptr))
    return numpy.ctypeslib.as_array(array_buf, shape=(rows, cols))

def _image_u8_get_array(img_ptr):
    return _ptr_to_array2d(ctypes.c_uint8,
                           img_ptr.contents.buf.contents,
                           img_ptr.contents.height,
                           img_ptr.contents.stride)

def _matd_get_array(mat_ptr):
    return _ptr_to_array2d(ctypes.c_double,
                           mat_ptr.contents.data,
                           int(mat_ptr.contents.nrows),
                           int(mat_ptr.contents.ncols))

######################################################################

DetectionBase = collections.namedtuple(
    'DetectionBase',
    'tag_family, tag_id, hamming, goodness, decision_margin, '
    'homography, center, corners')

class Detection(DetectionBase):

    '''Pythonic wrapper for apriltag_detection which derives from named
tuple class.

    '''

    _print_fields = [
        'Family', 'ID', 'Hamming error', 'Goodness',
        'Decision margin', 'Homography', 'Center', 'Corners'
    ]

    _max_len = max(len(field) for field in _print_fields)

    def tostring(self, indent=0):

        '''Converts this object to a string with the given level of indentation.'''

        rval = []
        indent_str = ' '*(self._max_len+2+indent)

        for i, label in enumerate(self._print_fields):

            value = str(self[i])

            if value.find('\n') > 0:
                value = value.split('\n')
                value = [value[0]] + [indent_str+v for v in value[1:]]
                value = '\n'.join(value)

            rval.append('{:>{}s}: {}'.format(
                label, self._max_len+indent, value))

        return '\n'.join(rval)

    def __str__(self):
        return self.tostring()

######################################################################


class DetectorOptions(object):

    '''Convience wrapper for object to pass into Detector
initializer. You can also pass in the output of an
argparse.ArgumentParser on which you have called add_arguments.

    '''

# pylint: disable=R0902
# pylint: disable=R0913

    def __init__(self,
                 families='tag36h11',
                 border=1,
                 nthreads=4,
                 quad_decimate=1.0,
                 quad_blur=0.0,
                 refine_edges=True,
                 refine_decode=False,
                 refine_pose=False,
                 debug=False,
                 quad_contours=True):

        self.families = families
        self.border = int(border)

        self.nthreads = int(nthreads)
        self.quad_decimate = float(quad_decimate)
        self.quad_sigma = float(quad_blur)
        self.refine_edges = int(refine_edges)
        self.refine_decode = int(refine_decode)
        self.refine_pose = int(refine_pose)
        self.debug = int(debug)
        self.quad_contours = quad_contours


######################################################################

class Detector(object):

    '''Pythonic wrapper for apriltag_detector. Initialize by passing in
the output of an argparse.ArgumentParser on which you have called
add_arguments; or an instance of the DetectorOptions class.'''

    def __init__(self, options=None):

        if options is None:
            options = DetectorOptions()

        self.options = options


        # detect OS to get extension for DLL
        uname0 = os.uname()[0]
        if uname0 == 'Darwin':
            extension = '.dylib'
        else:
            extension = '.so' # TODO test on windows?

        filename = 'libapriltag'+extension


        # load the C library and store it as a class variable
        # note: prefer OS install to local!
        try:
            self.libc = ctypes.CDLL(filename)
        except OSError:
            selfdir = os.path.dirname(__file__)
            #relpath = os.path.join(selfdir, '../build/lib/', filename)
            relpath = os.path.join(selfdir, filename)
            if not os.path.exists(relpath):
                """new edit starts"""
                # raise
                relpath = os.path.join(os.getcwd(), '../build/lib', filename)

                if not os.path.exists(relpath):
                    raise
                """new edit ends"""
            self.libc = ctypes.CDLL(relpath)
            
        # declare return types of libc function
        self._declare_return_types()

        # create the c-_apriltag_detector object
        self.tag_detector = self.libc.apriltag_detector_create()
        self.tag_detector.contents.nthreads = int(options.nthreads)
        self.tag_detector.contents.quad_decimate = float(options.quad_decimate)
        self.tag_detector.contents.quad_sigma = float(options.quad_sigma)
        self.tag_detector.refine_edges = int(options.refine_edges)
        self.tag_detector.refine_decode = int(options.refine_decode)
        self.tag_detector.refine_pose = int(options.refine_pose)

        if options.quad_contours:
            self.libc.apriltag_detector_enable_quad_contours(self.tag_detector, 1)

        self.families = []

        flist = self.libc.apriltag_family_list()

        for i in range(flist.contents.size):
            ptr = ctypes.c_char_p()
            self.libc.zarray_get(flist, i, ctypes.byref(ptr))
            self.families.append(ctypes.string_at(ptr))
		
        self.libc.apriltag_family_list_destroy(flist)  # sandeep's edit

        if options.families == 'all':
            families_list = self.families
        elif isinstance(options.families, list):
            families_list = options.families
        else:
            families_list = [n for n in re.split(r'\W+', options.families) if n]

        # add tags
        for family in families_list:
            self.add_tag_family(family)

    def __del__(self):  # sandeep edit
        self.libc.apriltag_detector_destroy(self.tag_detector)

    #@profile
    def detect(self, img, return_image=False):

        '''Run detectons on the provided image. The image must be a grayscale
image of type numpy.uint8.'''

        assert len(img.shape) == 2
        assert img.dtype == numpy.uint8

        c_img = self._convert_image(img)

        """new edits starts"""

        return_info = []
        import resource
        #detect apriltags in the image
        print "before", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        detections = self.libc.apriltag_detector_detect(self.tag_detector, c_img) #already in
        print "after", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

        #create a pytags_info object
        #return_info = []

        apriltag = ctypes.POINTER(_ApriltagDetection)()
        """new edit ends"""

        for i in range(0, detections.contents.size):

            #extract the data for each apriltag that was identified
            # apriltag = ctypes.POINTER(_ApriltagDetection)() # removed after new edit
            self.libc.zarray_get(detections, i, ctypes.byref(apriltag))

            tag = apriltag.contents

            homography = _matd_get_array(tag.H).copy()
            center = numpy.ctypeslib.as_array(tag.c, shape=(2,)).copy()
            corners = numpy.ctypeslib.as_array(tag.p, shape=(4, 2)).copy()

            detection = Detection(
                ctypes.string_at(tag.family.contents.name),
                tag.id,
                tag.hamming,
                tag.goodness,
                tag.decision_margin,
                homography,
                center,
                corners) # tag.family.contents.name, #sandeeps edit

            #Append this dict to the tag data array
            return_info.append(detection)
        """new edit starts"""
        # self.libc.image_u8_destroy(c_img) # doesn't work
        c_img = None
        """new edit ends"""
        if return_image:

            dimg = self._vis_detections(img.shape, detections)
            rval = return_info, dimg

        else:

            rval = return_info

        self.libc.apriltag_detections_destroy(detections)
        return rval


    def add_tag_family(self, name):

        '''Add a single tag family to this detector.'''

        family = self.libc.apriltag_family_create(name)

        if family:
            family.contents.border = self.options.border
            self.libc.apriltag_detector_add_family(self.tag_detector, family)
        else:
            print 'Unrecognized tag family name. Try e.g. tag36h11'

    def _vis_detections(self, shape, detections):

        height, width = shape
        c_dimg = self.libc.image_u8_create(width, height)
        self.libc.apriltag_vis_detections(detections, c_dimg)
        tmp = _image_u8_get_array(c_dimg)
        """new edit starts"""

        rval = tmp[:, :width].copy()

        self.libc.image_u8_destroy(c_dimg)

        #return tmp[:, :width].copy()
        return rval
    """new edit ends"""

    def _declare_return_types(self):

        self.libc.apriltag_detector_create.restype = ctypes.POINTER(_ApriltagDetector)
        self.libc.apriltag_family_create.restype = ctypes.POINTER(_ApriltagFamily)
        self.libc.apriltag_detector_detect.restype = ctypes.POINTER(_ZArray)
        self.libc.image_u8_create.restype = ctypes.POINTER(_ImageU8)
        self.libc.image_u8_write_pnm.restype = ctypes.c_int
        self.libc.apriltag_family_list.restype = ctypes.POINTER(_ZArray)
        self.libc.apriltag_vis_detections.restype = None

    def _convert_image(self, img):

        height = img.shape[0]
        width = img.shape[1]
        c_img = self.libc.image_u8_create(width, height)

        tmp = _image_u8_get_array(c_img)

        # copy the opencv image into the destination array, accounting for the
        # difference between stride & width.
        tmp[:, :width] = img

        # tmp goes out of scope here but we don't care because
        # the underlying data is still in c_img.
        return c_img

######################################################################

