import time
import cv2
import numpy as np
import os

# path to sturdy-robot-passer/ folder
root = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    os.pardir,
    os.pardir,
)

# generate ChAruco Borad
dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_50)
board = cv2.aruco.CharucoBoard_create(5, 7, 1, .8, dictionary)
pixel_border = 50
img = board.draw((2100, 2970), borderBits=1, marginSize=pixel_border)


# Dump the calibration board to a file
charuco_filepath = os.path.join(
    root,
    'resources',
    'aruco',
    'charuco.jpg'
)
cv2.imwrite(charuco_filepath, img)


img_tag30 = cv2.aruco.drawMarker(dictionary, 30, 600)
img_tag31 = cv2.aruco.drawMarker(dictionary, 31, 600)

tag30_filepath = os.path.join(
    root,
    'resources',
    'aruco',
    'tag30.png'
)
tag31_filepath = os.path.join(
    root,
    'resources',
    'aruco',
    'tag31.png'
)

cv2.imwrite(tag30_filepath, img_tag30)
cv2.imwrite(tag31_filepath, img_tag31)
