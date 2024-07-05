from decord import cpu, gpu
from decord import VideoReader, AVReader
import cv2
import numpy as np
import os
import yaml
import argparse
import PySimpleGUI as sg
import sys


parser = argparse.ArgumentParser(description="tag videos",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    "folder_path", help="Relative path (to the current folder) to the folder containing the video files are stored")
parser.add_argument(
    "info_path", help="Name of the file (YAML) in which to store the info")
parser.add_argument(
    "-st", "--start", help="Name of the video (without the extension) to start from (alphabetically)")
parser.add_argument(
    "-sk", "--skip", nargs="*", type=str, default=[], help="Names of the videos (without the extension) to skip")

args = parser.parse_args()

config = vars(args)

cwd = os.getcwd()
target_yaml_path = os.path.join(
    cwd,
    config['info_path']
)

video_folder_path = os.path.join(
    cwd,
    config['folder_path']
)

videos_to_skip = config['skip']
print(f"Skipping videos:\n{videos_to_skip}")


if not os.path.exists(video_folder_path):
    raise ValueError("The selected folder does not exists")

if not target_yaml_path.endswith(".yaml"):
    raise ValueError("The target file should have *.yaml extension")

if os.path.exists(target_yaml_path):
    raise ValueError("The target file already exists")


# search names and path of available videos
videos_list = []
for subdirs, dirs, files in os.walk(video_folder_path):
    for file in files:
        if file.endswith((".MP4",)):

            name = file.split('.')[0]
            video_path = os.path.join(video_folder_path, file)

            videos_list.append((name, video_path))

# sort alphabetically
videos_list.sort(key=lambda y: y[0])

# index of the video to start with
if config['start'] is None:
    idx_start = 0
else:
    name_list = [info[0] for info in videos_list]
    try:
        idx_start = name_list.index(config['start'])
    except ValueError:
        raise ValueError("The video selected to start does not exists")


# # # PySimpleGUI
# Set theme
sg.theme('BluePurple')


def LEDIndicator(key=None, radius=30):
    return sg.Graph(canvas_size=(radius, radius),
                    graph_bottom_left=(-radius, -radius),
                    graph_top_right=(radius, radius),
                    pad=(0, 0), key=key)


def SetLED(window, key, color):
    graph = window[key]
    graph.erase()
    graph.draw_circle((0, 0), 12, fill_color=color, line_color=color)


def save():
    with open(target_yaml_path, 'w') as f:
        yaml.dump(videos_info_dict, f)


# function to apply to each frame before showing it
def filterFrame(frame):
    frame = cv2.resize(frame, (860, 640))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = np.dstack([frame, frame, frame])
    return frame


# dict to fill with the info given by the user
videos_info_dict = {}


for i in range(idx_start, len(videos_list)):
    # retrieve info
    name = videos_list[i][0]
    video_path = videos_list[i][1]

    if name in videos_to_skip:
        # go to next video if this one is to be skipped
        continue

    print(f"Processing video: {name}")

    videos_info_dict[name] = {
        'marked frames': set(),
        'bad': False
    }

    # load video
    vr = VideoReader(video_path, ctx=cpu(0))
    # and convert it to numpy
    v = vr[:].asnumpy()

    # ---===--- define the window layout --- #
    layout = [[sg.Image(filename='', key='-image-')],

              [sg.Text(text="Marked"),
              LEDIndicator(key='-marked-', radius=50)],
              #   [sg.Slider(range=(0, len(vr)),
              #              size=(60, 10), orientation='h', key='-slider-')],

              [sg.Text(text="Frame", key='-frame-')],

              [sg.VSeparator(),
               sg.Button('<', size=(10, 3),
                         font='Helvetica 14', key='-back-'),
               sg.VSeparator(),
               sg.Button('>', size=(10, 3),
                         font='Helvetica 14', key='-forward-'),
               sg.Button('Think, Mark!', size=(8, 3), button_color=('gold', 'blue'),
                         font='Helvetica 14', key='-mark-'),
               sg.Button('Bad video\nno donuts', size=(8, 3), button_color=('black', 'red'),
                         font='Helvetica 10', key='-bad-'),
               sg.Button('Next video', size=(8, 2), pad=((200, 0), 0), button_color=('white', 'black'),
                         font='Helvetica 12', key='-next_video-'), ],

              [sg.Button('Exit', size=(5, 1), pad=((600, 0), 3), font='Helvetica 10')]]

    # create the window and show it without the plot
    window = sg.Window('Mark the frame(s) in which the clap-clap closes',
                       layout, no_titlebar=False, location=(100, 100), finalize=True)
    button_color = ('white', 'green')

    # locate the elements we'll be updating. Does the search only 1 time
    image_elem = window['-image-']
    frame_elem = window['-frame-']
    back_elem = window['-back-']
    forward_elem = window['-forward-']
    mark_elem = window['-mark-']
    next_vid_elem = window['-next_video-']

    # cv2.imshow(str(i), vr[15])
    # Loop
    # current frame selected
    j = 0
    frame = filterFrame(v[j])
    imgbytes = cv2.imencode('.png', frame)[1].tobytes()
    image_elem.update(data=imgbytes)
    frame_elem.update(f"Current frame: {j}/{v.shape[0]}")
    while True:
        event, values = window.read(timeout=10)

        # if frame j-th has been marked, set the led to green, and red otherwise
        if videos_info_dict[name]['bad']:
            SetLED(window, '-marked-', 'yellow')
        else:
            if j in videos_info_dict[name]['marked frames']:
                SetLED(window, '-marked-', 'green')
            else:
                SetLED(window, '-marked-', 'red')

        if event == 'Exit':
            window.close()
            save()
            sys.exit("Goodbye!")
        if event == '-next_video-':
            window.close()
            break
        if event == '-forward-':
            j = min(j+6, len(vr)-1)
            frame = filterFrame(v[j])
            imgbytes = cv2.imencode('.png', frame)[1].tobytes()
            image_elem.update(data=imgbytes)
            frame_elem.update(f"Current frame: {j}/{v.shape[0]}")
        if event == '-back-':
            j = max(j-6, 0)
            frame = filterFrame(v[j])
            imgbytes = cv2.imencode('.png', frame)[1].tobytes()
            image_elem.update(data=imgbytes)
            frame_elem.update(f"Current frame: {j}")
        if event == '-mark-':
            if not (j in videos_info_dict[name]['marked frames']):
                videos_info_dict[name]['marked frames'].add(j)
                SetLED(window, '-marked-', 'green')
            else:
                videos_info_dict[name]['marked frames'].remove(j)
                SetLED(window, '-marked-', 'red')
        if event == '-bad-':
            videos_info_dict[name]['bad'] = (not videos_info_dict[name]['bad'])

        if videos_info_dict[name]['marked frames']:
            next_vid_elem.update(button_color=('white', 'green'))
        else:
            next_vid_elem.update(button_color=('white', 'black'))
    save()

# # def filterFrame(frame):
# #     frame = cv2.resize(frame, (860, 640))
# #     return frame


# # vr = VideoReader(video_path, ctx=cpu(0))
# # v = vr[:].asnumpy()


# # i = 0
# # stop = False
# # while i<len(vr) and (not stop):
# #     frame = filterFrame(v[i])

# # for i in range(0, len(vr)):
# #     # the video reader will handle seeking and skipping in the most efficient manner
# #     frame = filterFrame(v[i])

# #     corners, ids, rejected = cv2.aruco.detectMarkers(
# #         frame, arucoDict, parameters=arucoParams)

# #     # verify *at least* one ArUco marker was detected
# #     if len(corners) > 0:
# #         # flatten the ArUco IDs list
# #         ids = ids.flatten()

# #         # loop over the detected ArUCo corners
# #         for (markerCorner, markerID) in zip(corners, ids):
# #             # extract the marker corners (which are always returned in
# #             # top-left, top-right, bottom-right, and bottom-left order)
# #             corners = markerCorner.reshape((4, 2))
# #             (topLeft, topRight, bottomRight, bottomLeft) = corners

# #             # convert each of the (x, y)-coordinate pairs to integers
# #             topRight = (int(topRight[0]), int(topRight[1]))
# #             bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
# #             bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
# #             topLeft = (int(topLeft[0]), int(topLeft[1]))

# #             # draw the bounding box of the ArUCo detection
# #             cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
# #             cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
# #             cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
# #             cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)

# #             # compute and draw the center (x, y)-coordinates of the ArUco
# #             # marker
# #             cX = int((topLeft[0] + bottomRight[0]) / 2.0)
# #             cY = int((topLeft[1] + bottomRight[1]) / 2.0)
# #             cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)

# #     frame = cv2.resize(frame, (860, 640))
# #     cv2.imshow(str(i), frame)
# #     # print(frame.shape)
# #     cv2.waitKey(0)
# #     cv2.destroyAllWindows()

# # # # # To get multiple frames at once, use get_batch
# # # # # this is the efficient way to obtain a long list of frames
# # # # frames = vr.get_batch([1, 3, 5, 7, 9])
# # # # print(frames.shape)
# # # # # (5, 240, 320, 3)
# # # # # duplicate frame indices will be accepted and handled internally to avoid duplicate decoding
# # # # frames2 = vr.get_batch([1, 2, 3, 2, 3, 4, 3, 4, 5]).asnumpy()
# # # # print(frames2.shape)
# # # # # (9, 240, 320, 3)

# # # # # 2. you can do cv2 style reading as well
# # # # # skip 100 frames
# # # # vr.skip_frames(100)
# # # # # seek to start
# # # # vr.seek(0)
# # # # batch = vr.next()
# # # # print('frame shape:', batch.shape)
# # # # print('numpy frames:', batch.asnumpy())
