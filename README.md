# Stereo RealSense

Package containing the material for using 3D stereo vision with realsenses cameras.

## Example Pipeline

### 1 Check the view in your cameras

Either using ```$ realsense-viewer``` or the script ```stereo_realsense/scripts/calibration/show_rgb_stream.py```

### 2 Record calibration video from connected cameras

Default settings (can be changed by changing the script directly):

- video are saved in MKV format with H264 codec.
- resolution is set to (1280,720)
- frame rate 30fps

To record the video (use multiple ```--id``` tags, one for each camera to record from):

```console
$ python3 $(rospack find stereo_realsense)/scripts/calibration/record_calibration.py --path <path-to-folder-where-to-save-videos> --id [serial number of camera 1] --id [serial number of camera 2] --id [serial number of camera N-th]
```

Note: video are saved with name formed by *DateTime_CameraSerialN.mkv*

### 3 Extract calibration images from videos

DeepLabCut suggests 30-70 frames per camera.

Example command to extract one frame every 0.2 second

```console
$ ffmpeg -i DateTime_CameraSerialN.mkv -vf fps=1/0.2 DateTime_CameraSerialN_%04d.png
```

e.g.

```console
ffmpeg -i 06062023161800_213322074048.mkv -vf fps=1/0.2 06062023161800_213322074048_%04d.png
```

### 4 Calibrate individual cameras (just once)

Use script as s
```console
$ python3 $(rospack find stereo_realsense)/scripts/calibration/single_camera_calibrate.py --framepath <folder-with-images-of-ONLY-one-camera>/  --format png --configpath <file-where-to-save-calibration-data> --id <camera_serial_number-or_just_a_name>
```
e.g.
```console
python3 $(rospack find stereo_realsense)/scripts/calibration/single_camera_calibrate.py --framepath /home/apab/Documents/calibration/single_camera_frames/213322070131/  --format png --configpath $(rospack find stereo_realsense)/config/ --id 213322070131
```
the calibration matrix and distortion coefficients are saved in a JSON file in the folder passed as --configpath

### 5 Check camera alignement
