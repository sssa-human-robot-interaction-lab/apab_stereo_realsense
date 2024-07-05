import os
import numpy as np
import cv2
import argparse
import json
import matplotlib.pyplot as plt
from datetime import datetime

parser = argparse.ArgumentParser("single_camera_calibration")
parser.add_argument("--framepath", type=str, help="Location where the calibration frames are saved", required=True)
parser.add_argument("--configpath", type=str, help="Location where the instrinsic calibration parameters are stored, for each camera, in JSON format", required=True)
parser.add_argument("--format", type=str, default="png", choices=['png', 'jpg'], help="Format of image files to process (png, jpg, or jpeg)", required=True)
parser.add_argument('--id', action='append', help='ID of the cameras being considered, used to distinguish frames', required=True)

args = parser.parse_args()

### Parse all images in the directory
frames = {id : [] for id in args.id}

# check also which files belong to which camera, and if they're imported in the correct order
cam_filenames = {id : [] for id in args.id}

for file in sorted(os.listdir(args.framepath)):
    if file.endswith("." + args.format):
        f = cv2.imread(os.path.join(args.framepath, file), 1)
        id_file = file.split("_")[1]
        frames[id_file].append(f) 
        cam_filenames[id_file].append(file)

for i, k in enumerate(frames.keys()):
    print(f"Cam {i} - ID: {k}")
    print("Files:")
    print(cam_filenames[k])

if not (len(frames.keys()) == len(args.id)):
    raise ValueError


### Detect ChArUco in all images

# Set dictionary and recreate the board
### WARNING: the dictionary and board should match the one used to generated the Charuco board that is contained in the frames !!! ###
cols = 5
rows = 7
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_50)
board = cv2.aruco.CharucoBoard_create(cols, rows, 1, .8, aruco_dict)
# actual size [m] of a side of a black square, as printed in the final board
world_scaling = 0.04



allCorners = {id : [] for id in args.id}
allObjIds = {id : [] for id in args.id}
allObjPs = {id : [] for id in args.id}

# Sub pixel corner detection criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.00001)

# Objectpoints
objp = np.zeros(((rows-1)*(cols-1),3), np.float32)
# cursed
objp[:,:2] = np.mgrid[0:(cols-1), 0:(rows-1)].T.reshape(-1,2)
objp = world_scaling* objp

print("Detection of Charuco Board")


for i in range(len(frames[args.id[0]])):

    print(f"Frame {i}")

    gray = {id : [] for id in args.id}
    corners = {id : [] for id in args.id}
    obj_ids = {id : [] for id in args.id}
    rejectedImgPoints = {id : [] for id in args.id}

    # Detcet Aruco Tags
    for id in args.id:
        print(f"camera: {id}")
        gray[id] = cv2.cvtColor(frames[id][i], cv2.COLOR_BGR2GRAY)
        corners[id], obj_ids[id], rejectedImgPoints[id] = cv2.aruco.detectMarkers(gray[id], aruco_dict)
    
    # If one camera has detected nothing, we do not proceed
    skip_frame = False
    for id in args.id:
        if obj_ids[id] is None:
            skip_frame = True
    if skip_frame:
        continue

    res2 = {id : [] for id in args.id}

    # Interpolate the position of the corners of the board
    for id in args.id:
        print(f"camera: {id}")

        # SUB PIXEL DETECTION
        for corner in corners[id]:
            cv2.cornerSubPix(gray[id], corner,
                                winSize = (3,3),
                                zeroZone = (-1,-1),
                                criteria = criteria)
        
        res2[id] = list(cv2.aruco.interpolateCornersCharuco(corners[id],obj_ids[id],gray[id],board))

    # If one camera cannot interpolate to find any corner, we do not proceed
    skip_frame = False
    for id in args.id:
        if res2[id][2] is None:
            skip_frame = True
    if skip_frame:
        continue

    # List with set (actual Python set) of object identified by each camera
    obj_id_all_cams = [set(tuple(res2[id][2].reshape(-1))) for id in args.id]

    # Intersection: list of IDs of objects that have been identified by every camera
    obj_id_all_cams = list(set.intersection(*obj_id_all_cams))

    for id in args.id:
        
        # for the current camera, find the indices of objects seen also by all other cameras (index in the list res2[id][1] and res2[id][1])
        idx_obj_cam = [res2[id][2].tolist().index(obj) for obj in obj_id_all_cams]

        res2[id][1] = res2[id][1][idx_obj_cam]
        res2[id][2] = res2[id][2][idx_obj_cam]

        if res2[id][1] is not None and res2[id][2] is not None: # and len(res2[id][1])>3:
            allCorners[id].append(res2[id][1])
            allObjIds[id].append(res2[id][2])
            # append Objectpoints ony for the corner that has been identified, which are the number contained in "obj_ids"
            allObjPs[id].append(objp[res2[id][2].reshape(-1)])

print(allObjPs[args.id[0]][56]- allObjPs[args.id[1]][56])
print(allCorners[args.id[0]][56]- allCorners[args.id[1]][56])
print(np.array(allCorners[args.id[0]][56]).shape)


imsize = gray[args.id[0]].shape

# Import intrinsic calibration (distortion coefficient and camera matrix)
dist_coeff = {id : [] for id in args.id}
cam_mtx = {id : [] for id in args.id}
for id in args.id:
    configpath = os.path.join(args.configpath, f"intrinsic_camera_{id}.json")
    with open(configpath) as configfile:
        configparams = json.load(configfile)
        dist_coeff[id] = np.array(configparams["dist_coeff"])
        cam_mtx[id] = np.array(configparams["camera_matrix"])

print("Camera calibration")
# fix the intrinsic, it has already been computed (should produce a better estimate)
stereocalibration_flags = cv2.CALIB_FIX_INTRINSIC

# order of output is probably wrong?
ret, CM1, dist1, CM2, dist2, R, T, E, F = cv2.stereoCalibrate(allObjPs[args.id[0]], allCorners[args.id[0]], allCorners[args.id[1]], cam_mtx[args.id[0]], dist_coeff[args.id[0]],
    cam_mtx[args.id[1]], dist_coeff[args.id[1]], imsize, criteria = criteria, flags = stereocalibration_flags)

# print(dist_coeff[args.id[0]])
# print(dist_coeff[args.id[0]]-dist1)
# print(dist1)

print(f"Calibration executed, RMSE: {ret}")
# Convert to list (needed for JSON) and save in JSON
data = {
    "camera_order": args.id,
    "R": R.tolist(),
    "T": T.tolist()
    }

dt = datetime.now().strftime("%d%m%Y%H%M%S")

filename = f"extrinsic_{dt}_{args.id[0]}_{args.id[1]}.json"

with open(os.path.join(args.configpath, filename), "w") as f:
    json.dump(data, f)

print(f"Stereo calibration saved in {os.path.join(args.configpath, filename)}")
