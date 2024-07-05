from decord import cpu, gpu
from decord import VideoReader, AVReader
import cv2
import numpy as np
import os
import time
import imutils

# path to sturdy-robot-passer/
root = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    os.pardir,
    os.pardir,
)

video_folder = os.path.join(
    root,
    'data',
    'boiler_room_special',
    'video',
)

video_path = os.path.join(
    video_folder,
    'C0700.MP4'
)


def filterFrame(frame):
    frame = cv2.resize(frame, (860, 640))
    return frame


vr = VideoReader(video_path, ctx=cpu(0))
v = vr[:].asnumpy()


i = 0
stop = False
while i < len(vr) and (not stop):
    frame = filterFrame(v[i])

for i in range(0, len(vr)):
    # the video reader will handle seeking and skipping in the most efficient manner
    frame = filterFrame(v[i])

    corners, ids, rejected = cv2.aruco.detectMarkers(
        frame, arucoDict, parameters=arucoParams)

    # verify *at least* one ArUco marker was detected
    if len(corners) > 0:
        # flatten the ArUco IDs list
        ids = ids.flatten()

        # loop over the detected ArUCo corners
        for (markerCorner, markerID) in zip(corners, ids):
            # extract the marker corners (which are always returned in
            # top-left, top-right, bottom-right, and bottom-left order)
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners

            # convert each of the (x, y)-coordinate pairs to integers
            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))

            # draw the bounding box of the ArUCo detection
            cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
            cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
            cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
            cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)

            # compute and draw the center (x, y)-coordinates of the ArUco
            # marker
            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)
            cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)

    frame = cv2.resize(frame, (860, 640))
    cv2.imshow(str(i), frame)
    # print(frame.shape)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# # # To get multiple frames at once, use get_batch
# # # this is the efficient way to obtain a long list of frames
# # frames = vr.get_batch([1, 3, 5, 7, 9])
# # print(frames.shape)
# # # (5, 240, 320, 3)
# # # duplicate frame indices will be accepted and handled internally to avoid duplicate decoding
# # frames2 = vr.get_batch([1, 2, 3, 2, 3, 4, 3, 4, 5]).asnumpy()
# # print(frames2.shape)
# # # (9, 240, 320, 3)

# # # 2. you can do cv2 style reading as well
# # # skip 100 frames
# # vr.skip_frames(100)
# # # seek to start
# # vr.seek(0)
# # batch = vr.next()
# # print('frame shape:', batch.shape)
# # print('numpy frames:', batch.asnumpy())
