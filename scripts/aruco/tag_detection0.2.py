from decord import cpu, gpu
from decord import VideoReader, AVReader, AudioReader
import cv2
import numpy as np
import os
import time
import imutils
import plotly.graph_objects as go
from scipy import signal

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


def filterFrame(frame):
    frame = cv2.resize(frame, (860, 640))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = np.dstack([frame, frame, frame])
    return frame


vr = VideoReader(video_path, ctx=cpu(0))
ar = AudioReader(video_path, ctx=cpu(0), mono=True)

# convert to numpy array
a = ar[:].asnumpy()[0]
v = vr[:].asnumpy()
print(a)
print(a.shape)
# print(ar.sample_rate)

# audio spectrogram
f, t, Sxx = signal.spectrogram(a)

fig = go.Figure()
fig.add_trace(go.Scatter(
    y=a,
    # text=df['country'][start:end],
    mode='markers',
    # marker=dict(
    #     # sizemode='diameter',
    #     # sizeref=50,
    #     size=4,
    #     color=r_color,
    #     colorscale=colorscale,
    #     colorbar_title='err',
    #     # line_color='rgb(140, 140, 170)',
    #     # cmin=-1,
    #     # cmax=1,
    #     showscale=True  # if (scenario=='all') else False
    # ),
    # name='Robot'
))
fig.show()

fig2 = go.Figure()
fig2.add_trace(go.Heatmap(
    x=f,
    y=t,
    z=Sxx,
    # colorscale='bluered',
    # zmin=-1.0,
    # zmax=1.0,
))
fig2.show()


# # a file like object works as well, for in-memory decoding
# # with open(video_path, 'rb') as f:
# #     vr = VideoReader(f, ctx=cpu(0))

# print('video frames:', len(vr))
# # 1. the simplest way is to directly access frames
# for i in range(len(vr)):
#     # the video reader will handle seeking and skipping in the most efficient manner
#     frame = vr[i]
#     frame = filterFrame(frame.asnumpy())
#     cv2.imshow(str(i), frame)
#     # print(frame.shape)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()

# # To get multiple frames at once, use get_batch
# # this is the efficient way to obtain a long list of frames
# frames = vr.get_batch([1, 3, 5, 7, 9])
# print(frames.shape)
# # (5, 240, 320, 3)
# # duplicate frame indices will be accepted and handled internally to avoid duplicate decoding
# frames2 = vr.get_batch([1, 2, 3, 2, 3, 4, 3, 4, 5]).asnumpy()
# print(frames2.shape)
# # (9, 240, 320, 3)

# # 2. you can do cv2 style reading as well
# # skip 100 frames
# vr.skip_frames(100)
# # seek to start
# vr.seek(0)
# batch = vr.next()
# print('frame shape:', batch.shape)
# print('numpy frames:', batch.asnumpy())
