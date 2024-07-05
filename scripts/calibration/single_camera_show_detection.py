import os
import numpy as np
import cv2
import argparse
import json
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser("single_camera_show_detection")
parser.add_argument("--framepath", type=str, help="Location where the calibration frames are saved", required=True)
parser.add_argument("--format", type=str, default="png", choices=['png', 'jpg'], help="Format of image files to process (png, jpg, or jpeg)", required=True)

args = parser.parse_args()

### Parse all images in the directory
frames = []
for file in os.listdir(args.framepath):
    if file.endswith("." + args.format):
        f = cv2.imread(os.path.join(args.framepath, file), 1)
        frames.append(f)
print(f"{len(frames)} frames found")


### Detect ChArUco in all images

# Set dictionary and recreate the board
### WARNING: the dictionary and board should match the one used to generated the Charuco board that is contained in the frames !!! ###
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_50)
board = cv2.aruco.CharucoBoard_create(5, 7, 1, .8, aruco_dict)



allCorners = []
allIds = []

# Sub pixel corner detection criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.00001)

print("Detection of Charuco Board")

for frame in frames:

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, aruco_dict)

    if len(corners)>0:
        # SUB PIXEL DETECTION
        for corner in corners:
            cv2.cornerSubPix(gray, corner,
                                winSize = (3,3),
                                zeroZone = (-1,-1),
                                criteria = criteria)
        res2 = cv2.aruco.interpolateCornersCharuco(corners,ids,gray,board)
        if res2[1] is not None and res2[2] is not None and len(res2[1])>3:
            allCorners.append(res2[1])
            allIds.append(res2[2])
        
        # Draw and display the corners
        cv2.aruco.drawDetectedCornersCharuco(frame, res2[1], res2[2])
        cv2.imshow('img', frame)
        cv2.waitKey(10000)


imsize = gray.shape


