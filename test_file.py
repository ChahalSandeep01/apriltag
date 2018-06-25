#!/usr/bin/env python

# Copyright 2015 Fetch Robotics Inc.
# Author: Sandeep Chahal
# Issues:
# excessive memory usage -. possible memory leak
# [h264 @ 0x3998080] mmco: unref short failure
# [h264 @ 0x3998080] illegal short term buffer state detected
# RuntimeWarning: Item size computed from the PEP 3118 buffer format string does not match the actual item size. return array(obj, copy=False)


## @file change in april tag

import cv2
import apriltag
from time import gmtime, strftime
import time
import json
import sys
import matplotlib.pyplot as plt
import ctypes
# import objgraph
import gc
import os


import resource

#afffb8b842878a3b6c06fe533eda64d6625db4f3

#@profile
def main():

    print time.time()
    capt = cv2.VideoCapture('rtsp://admin:Robotslikevideo@hik5/Streaming/Channels/1')

    # 10 frames per second
    # fps = capt.get(cv2.CAP_PROP_FPS)
    # print fps
    # if capt.isOpened():
    #     ret, frame = capt.read()
    #     my_image = frame

    # track_list_position=[]
    #
    # try:
    #     with open("track_list.json") as json_file:
    #           my_list = json.load(json_file)
    #     # with open("track_list.json", 'w') as outfile:
    #     #      json.dump(track_list_position, outfile)

    track_list_position = []
    track_list_time = []
    mycount = 0

    detec = apriltag.Detector()   # explodes memory if declared in loop or called in loop

    area = None
    memory_report_1 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    memory_report_2 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    print "before while loop; ", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


    while capt.isOpened(): #and mycount < 200:
        print mycount
        if memory_report_1 != memory_report_2:
            print "come here"
            print "restart my script"
            #os.execv('/home/fetch/PycharmProjects/memtest/sandeep.py', [''])  # restart my script

        ret, frame = capt.read()

        #resizing can help execution faster and less memory leak
        #frame = cv2.resize(frame, (800, 1024))

        #converting image to gray
        if len(frame.shape) == 3 or len(frame.shape) == 4:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        memory_report_1 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

        # detecting the codes in image
        detected_codes_in_image = detec.detect(frame)

        memory_report_2 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

        mycount += 1

        #area = [detected_codes_in_image[0].center[0], detected_codes_in_image[0].center[1]]

        # for a single tag
        print detected_codes_in_image[0]
        # if detected_codes_in_image:
        #     temp_dict = {"tag_id": detected_codes_in_image[0].tag_id,
        #                  "tag_area": [[detected_codes_in_image[0].corners[0][0], detected_codes_in_image[0].corners[0][1]],
        #                                                [detected_codes_in_image[0].corners[1][0], detected_codes_in_image[0].corners[1][1]],
        #                                                [detected_codes_in_image[0].corners[2][0], detected_codes_in_image[0].corners[2][1]],
        #                                                [detected_codes_in_image[0].corners[3][0], detected_codes_in_image[0].corners[3][1]]],
        #                  "center": [tag.center[0], tag.center[1]], "cam_no": camera_number}
        #     # track_list_positio: n.append([detected_codes_in_image[0].center[0], detected_codes_in_image[0].center[1]])
        #     cv2.rectangle(frame, (int(detected_codes_in_image[0].corners[0][0]),
        #                           int(detected_codes_in_image[0].corners[0][1])),
        #                   (int(detected_codes_in_image[0].corners[2][0]),
        #                    int(detected_codes_in_image[0].corners[2][1])), (0, 0, 255), 3)
        #     # cv2.circle(my_image, (int(detected_codes_in_image[0].center[0]), int(detected_codes_in_image[0].center[1])), 1, (0, 255, 255))

        #detec.destroy_tag(detected_codes_in_image)

        print "resources", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

        # resize to display window normal
        # frame = cv2.resize(frame, (960, 540))
        # print (frame.shape)
        cv2.imshow('scaled_image', frame)

        mycount += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == '__main__':
        main()
"""  DEALING WITH MEMORY LEAK
def dump_garbage():

    #show us what's the garbage about


    # force collection
    print "\nGARBAGE:"
    gc.collect()

    print "\nGARBAGE OBJECTS:"
    for x in gc.garbage:
        s = str(x)
        if len(s) > 80: s = s[:80]
        print type(x), "\n  ", s


def zeromem(gray):
    detec = apriltag.Detector()
    # print "size of det", sys.getsizeof(detec)
    san = detec.detect(gray)
    # print "size of san", sys.getsizeof(san)
    van = san[:]
    del detec
    del san
    # print "Clearing ", (detec, san)
    memset = ctypes.CDLL("libc.so.6").memset
    return van

def zeroone(gray):
    sb = zeromem(gray)
    return sb

while capt.isOpened and x < 1:
    start_time = time.time()
    ret, frame = capt.read()
    # converting image to gray scale
    # frame = cv2.resize(frame, (1000, 500))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # detecting a tag
    import gc


    detected_codes_in_image = zeroone(gray)

    import resource

    mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print 'before memset', mem

    # Collecting now keeps the objects as uncollectable
    n = gc.collect()

    print "unreachable objects : ", n           # unreachable objects 94
    print 'Remaining Garbage : ', gc.garbage
    #gc.garbage[0].set_next()

    REFERRERS_TO_IGNORE = [locals(), globals(), gc.garbage]


    def find_referring_graphs(obj):
        print 'Looking for references to %s' % repr(obj)
        referrers = (r for r in gc.get_referrers(obj)
                     if r not in REFERRERS_TO_IGNORE)
        for ref in referrers:
            if isinstance(ref, zeroone):
                # A graph node
                yield ref
            elif isinstance(ref, dict):
                # An instance or other namespace dictionary
                for parent in find_referring_graphs(ref):
                    yield parent

    for obj in gc.garbage:
        for ref in find_referring_graphs(obj):
            ref.set_next(None)
            del ref  # remove local reference so the node can be deleted
        del obj  # remove local reference so the node can be deleted

    # gc.set_debug(gc.DEBUG_STATS)
    n = gc.collect()
    print "unreachable objects : ", n
    mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print 'after memset', mem
    #forcing a sweep
    print 'collecting...'
    gc.collect()
    print 'done'
    for o in gc.garbage:
        if isinstance(o, zeroone):
            print 'Retained: %s 0x%x' % (o, id(o))
    print gc.get_threshold()
    print x
    x +=1


    #detected_codes_in_image = detec.detect(gray)
    # area = [detected_codes_in_image[0].center[0], detected_codes_in_image[0].center[1]]

    # for a single tag
    # print detected_codes_in_image[0]

    # if detected_codes_in_image:
    #     track_list_position.append([detected_codes_in_image[0].center[0], detected_codes_in_image[0].center[1]])
    #     cv2.rectangle(frame, (int(detected_codes_in_image[0].corners[0][0]),
    #                       int(detected_codes_in_image[0].corners[0][1])),
    #                  (int(detected_codes_in_image[0].corners[2][0]),
    #                   int(detected_codes_in_image[0].corners[2][1])), (0, 0, 255), 3)
    #     cv2.circle(my_image, (int(detected_codes_in_image[0].center[0]), int(detected_codes_in_image[0].center[1])), 1, (0, 255, 255))
    #
    #
    # resize to display window normal
    # frame = cv2.resize(frame, (960, 540))
    # #print (frame.shape)
    # cv2.imshow('scaled_image', my_image)

    # print 'before memset'
    #
    #
    # memory issue
    # import resource
    # mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # print 'before memset', mem
    #
    # # memset =  ctypes.CDLL("libc.so.6").memset  -> doesn't help
    # print 'after memset', mem
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break
    # gc.collect
    #objgraph.show_most_common_types()  -> doesn't show anything
    # memset = ctypes.CDLL("libc.so.6").memset -> doesnt work
    # time.sleep(0.50 - time.time() + start_time)



# with open("track_list.json", 'w') as outfile:
#      json.dump(track_list_position, outfile)
#
# with open("track_list.json") as json_file:
#      my_list = json.load(json_file)
#
# plt.imshow(my_image)
# for phiss in my_list:
#     plt.scatter(int(phiss[0]), int(phiss[1]))
# plt.show()
"""

"""after memset 744504
function                   10655
list                       4108
tuple                      3288
dict                       3063
wrapper_descriptor         2410
weakref                    1729
builtin_function_or_method 1664
method_descriptor          1658
cell                       1273
type                       1087
"""

"""after memset 3160120
function                   10839
list                       4796
dict                       2991
tuple                      2941
wrapper_descriptor         2410
weakref                    1809
builtin_function_or_method 1664
method_descriptor          1658
cell                       1285
getset_descriptor          1159"""