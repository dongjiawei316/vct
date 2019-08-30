# -*- coding: utf-8 -*-
import sys
from ipywidgets import interact
from matplotlib import pyplot as plt
import ffmpeg
import ipywidgets as widgets
import numpy as np
import time
from PIL import Image
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from cv2 import *
import _thread as thread

probe = ffmpeg.probe('resource/1.ts')
video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
width = int(video_info['width'])
height = int(video_info['height'])
#num_frames = int(video_info['nb_frames'])

mapp = QApplication(sys.argv)
win = QWidget()
pictureLabel = QLabel()
init_image = QPixmap("resource/cat.jpeg").scaled(640, 480)
pictureLabel.setPixmap(init_image)

layout = QVBoxLayout()
layout.addWidget(pictureLabel)

win.setLayout(layout)
win.show()
print("QWidget ok!")


process1 = (
    ffmpeg
    .input("resource/1.ts")
    .output('pipe:', format='rawvideo', pix_fmt='rgb24')
    .run_async(pipe_stdout=True)
)

def extract_frame(process1):
    while True:

        in_bytes = process1.stdout.read(width * height * 3)
        if not in_bytes:
            break

        in_frame = (
            np
                .frombuffer(in_bytes, np.uint8)
                .reshape([height, width,3])
        )

        frame = cv2.resize(in_frame, (640, 480))
        temp_image = QImage(frame, 640, 480, QImage.Format_RGB888)
        temp_pixmap = QPixmap.fromImage(temp_image)
        pictureLabel.setPixmap(temp_pixmap)
        time.sleep(0.04)


thread.start_new_thread( extract_frame, (process1, ) )

sys.exit(mapp.exec_())

process1.wait()




"""
from io import BytesIO
from PIL import Image


def extract_frame(stream, frame_num):
    while isinstance(stream, ffmpeg.nodes.OutputStream):
        stream = stream.node.incoming_edges[0].upstream_node.stream()
    out, _ = (
        stream
            .filter_('select', 'gte(n,{})'.format(frame_num))
            .output('pipe:', format='rawvideo', pix_fmt='rgb24', vframes=1)
            .run(capture_stdout=True, capture_stderr=True)
    )
    return np.frombuffer(out, np.uint8).reshape([height, width, 3])


def png_to_np(png_bytes):
    buffer = BytesIO(png_bytes)
    pil_image = Image.open(buffer)
    return np.array(pil_image)


def build_graph(
        enable_overlay, flip_overlay, enable_box, box_x, box_y,
        thickness, color):
    stream = ffmpeg.input('in.mp4')

    if enable_overlay:
        overlay = ffmpeg.input('overlay.png')
        if flip_overlay:
            overlay = overlay.hflip()
        stream = stream.overlay(overlay)

    if enable_box:
        stream = stream.drawbox(
            box_x, box_y, 120, 120, color=color, t=thickness)

    return stream.output('out.mp4')


def show_image(ax, stream, frame_num):
    try:
        image = extract_frame(stream, frame_num)
        ax.imshow(image)
        ax.axis('off')
    except ffmpeg.Error as e:
        print(e.stderr.decode())


def show_graph(ax, stream, detail):
    data = ffmpeg.view(stream, detail=detail, pipe=True)
    image = png_to_np(data)
    ax.imshow(image, aspect='equal', interpolation='hanning')
    ax.set_xlim(0, 1100)
    ax.axis('off')


@interact(
    frame_num=(0, num_frames),
    box_x=(0, 200),
    box_y=(0, 200),
    thickness=(1, 40),
    color=['red', 'green', 'magenta', 'blue'],
)
def f(
        enable_overlay=True,
        enable_box=True,
        flip_overlay=True,
        graph_detail=False,
        frame_num=0,
        box_x=50,
        box_y=50,
        thickness=5,
        color='red'):
    stream = build_graph(
        enable_overlay,
        flip_overlay,
        enable_box,
        box_x,
        box_y,
        thickness,
        color
    )

    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(15, 4))
    plt.tight_layout()
    show_image(ax0, stream, frame_num)
    show_graph(ax1, stream, graph_detail)
"""