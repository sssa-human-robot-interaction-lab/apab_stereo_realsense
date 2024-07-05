import argparse
from imutils.video import FPS
from imutils.video import FileVideoStream
import time
import cv2
import imutils
import numpy as np
import os

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
    'C0615.MP4'
)

# Modified from:
# https://www.pyimagesearch.com/2017/02/06/faster-video-file-fps-with-cv2-videocapture-and-opencv/


def filterFrame(frame):
    frame = imutils.resize(frame, width=450)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = np.dstack([frame, frame, frame])
    return frame


# start the file video stream thread and allow the buffer to
# start to fill
print("[INFO] starting video file thread...")
fvs = FileVideoStream(video_path, transform=filterFrame).start()
time.sleep(1.0)

cv2.imshow("Frame", fvs.Q[100])
time.sleep(30)

# start the FPS timer
fps = FPS().start()

# loop over frames from the video file stream
while fvs.running():
    # grab the frame from the threaded video file stream, resize
    # it, and convert it to grayscale (while still retaining 3
    # channels)
    frame = fvs.read()

    # Relocated filtering into producer thread with transform=filterFrame
    #  Python 2.7: FPS 92.11 -> 131.36
    #  Python 3.7: FPS 41.44 -> 50.11
    #frame = filterFrame(frame)

    # display the size of the queue on the frame
    cv2.putText(frame, "Queue Size: {}".format(fvs.Q.qsize()),
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # show the frame and update the FPS counter
    cv2.imshow("Frame", frame)

    cv2.waitKey(1)
    if fvs.Q.qsize() < 2:  # If we are low on frames, give time to producer
        time.sleep(0.001)  # Ensures producer runs now, so 2 is sufficient
    fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
fvs.stop()
