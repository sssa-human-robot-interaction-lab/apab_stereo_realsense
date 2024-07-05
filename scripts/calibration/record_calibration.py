import pyrealsense2 as rs
import numpy as np
import cv2
import argparse
from datetime import datetime
import os


parser = argparse.ArgumentParser("calibration_recording")

parser.add_argument("--path", type=str, help="Location where to save the recordings", required=True)
# Cameras ID, use like:
# python arg.py --id 1234 --id 2345
parser.add_argument('--id', action='append', help='IDs of the cameras to record from', required=True)



args = parser.parse_args()


def main():
    # Pizel size of recorded frames
    # WARN: must be compatible with realsense options
    res = (1280, 720)
    fps = 30

    # Configure depth and color streams for each camera
    pipelines = {}
    configs = {}
    for id in args.id:
        # Create pipeline and config for a camera
        p = rs.pipeline()
        c = rs.config()
        

        # Connect to the camera specified by the ID (serial number)
        c.enable_device(id)

        # Get device product line for setting a supporting resolution
        pipeline_wrapper = rs.pipeline_wrapper(p)
        pipeline_profile = c.resolve(pipeline_wrapper)
        device = pipeline_profile.get_device()
        device_product_line = str(device.get_info(rs.camera_info.product_line))
        # Check if RGB  is available
        found_rgb = False
        for s in device.sensors:
            if s.get_info(rs.camera_info.name) == "RGB Camera":
                found_rgb = True
                break
        if not found_rgb:
            print("The demo requires Color sensor")
            exit(0)

        # Enable stream and start pipeline
        c.enable_stream(rs.stream.color, res[0], res[1], rs.format.bgr8, fps)

        p.start(c)

        pipelines[id]=p
        configs[id]=c
    
    # Create writers to save video stream
    color_writers = {}
    prefix = datetime.now().strftime("%d%m%Y%H%M%S")
    for id in args.id:
        color_path = os.path.join(args.path, f"{prefix}_{id}.mkv")
        color_writers[id] = cv2.VideoWriter(color_path, cv2.VideoWriter_fourcc('x','2','6','4'), fps, res, 1)

    try:
        while True:
            frames = {}
            for id, pipeline in pipelines.items():
                camera_frames = pipeline.wait_for_frames()
                color_frame = camera_frames.get_color_frame()
                if not color_frame:
                    print("\nAAAAAAAAAAAAAAAAAA")
                frames[id]=color_frame
            
            #convert images to numpy arrays
            color_images = {}
            for id, color_frame in frames.items():
                color_images[id] = np.asanyarray(color_frame.get_data())
                color_writers[id].write(color_images[id])

            for id in args.id:
                cv2.imshow(f"Stream {id}", color_images[id])
            
            if cv2.waitKey(1) == ord("q"):
                break
    finally:
        for id in args.id:
            color_writers[id].release()
            pipelines[id].stop()


if __name__ == "__main__":
    main()


# ##############################################
# color_path = 'V00P00A00C00_rgb.avi'
# depth_path = 'V00P00A00C00_depth.avi'
# colorwriter = cv2.VideoWriter(color_path, cv2.VideoWriter_fourcc(*'XVID'), 30, (640,480), 1)
# depthwriter = cv2.VideoWriter(depth_path, cv2.VideoWriter_fourcc(*'XVID'), 30, (640,480), 1)

# pipeline.start(config)

# try:
#     while True:
#         frames = pipeline.wait_for_frames()
#         depth_frame = frames.get_depth_frame()
#         color_frame = frames.get_color_frame()
#         if not depth_frame or not color_frame:
#             continue
        
#         #convert images to numpy arrays
#         depth_image = np.asanyarray(depth_frame.get_data())
#         color_image = np.asanyarray(color_frame.get_data())
#         depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        
#         colorwriter.write(color_image)
#         depthwriter.write(depth_colormap)
        
#         cv2.imshow('Stream', depth_colormap)
        
#         if cv2.waitKey(1) == ord("q"):
#             break
# finally:
#     colorwriter.release()
#     depthwriter.release()
#     pipeline.stop()