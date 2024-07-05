import os
import numpy as np
import cv2
import argparse
import json
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser("single_camera_calibration")
parser.add_argument("--framepath", type=str, help="Location where the calibration frames are saved", required=True)
parser.add_argument("--configpath", type=str, help="Location where the calibration parameters will be saved, in JSON format", required=True)
parser.add_argument("--format", type=str, default="png", choices=['png', 'jpg'], help="Format of image files to process (png, jpg, or jpeg)", required=True)
parser.add_argument('--id', help='ID of the camera being considered, to be written in yaml file', required=True)

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


imsize = gray.shape


print("Camera calibration")

cameraMatrixInit = np.array([[ 1000.,    0., imsize[0]/2.],
                                [    0., 1000., imsize[1]/2.],
                                [    0.,    0.,           1.]])
distCoeffsInit = np.zeros((5,1))
flags = (cv2.CALIB_USE_INTRINSIC_GUESS + cv2.CALIB_RATIONAL_MODEL + cv2.CALIB_FIX_ASPECT_RATIO)
#flags = (cv2.CALIB_RATIONAL_MODEL)
(ret, camera_matrix, distortion_coefficients,
    rotation_vectors, translation_vectors,
    stdDeviationsIntrinsics, stdDeviationsExtrinsics,
    perViewErrors) = cv2.aruco.calibrateCameraCharucoExtended(
                    charucoCorners=allCorners,
                    charucoIds=allIds,
                    board=board,
                    imageSize=imsize,
                    cameraMatrix=cameraMatrixInit,
                    distCoeffs=distCoeffsInit,
                    flags=flags,
                    criteria=(cv2.TERM_CRITERIA_EPS & cv2.TERM_CRITERIA_COUNT, 10000, 1e-9))

# ret, camera_matrix, distortion_coefficients0, rotation_vectors, translation_vectors
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, distortion_coefficients, imsize, 1, imsize)
print(ret)
print(camera_matrix)
print(distortion_coefficients)
# print(rotation_vectors)
# print(translation_vectors)

# Convert to list (needed for JSON) and save in JSON
data = {"camera_matrix": camera_matrix.tolist(), "dist_coeff": distortion_coefficients.tolist()}
filename = f"intrinsic_camera_{args.id}.json"
with open(os.path.join(args.configpath, filename), "w") as f:
    json.dump(data, f)
print(f"Camera calibration saved in {os.path.join(args.configpath, filename)}")


# Plot calibration results
for frame in frames:
    plt.figure()
    img_undist = cv2.undistort(frame, camera_matrix, distortion_coefficients, None, newcameramtx)
    cv2.imshow(f"Original ", frame)
    cv2.imshow(f"Corrected", img_undist)

    if cv2.waitKey(0) == ord("q"):
        break
    elif cv2.waitKey(0) == ord("d"):
        continue

