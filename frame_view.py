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
import threading

# udp://192.165.53.18:22000
#probe = ffmpeg.probe('resource/1.ts')

mapp = QApplication(sys.argv)
win = QWidget()
pictureLabel = QLabel()
init_image = QPixmap("resource/cat.jpeg").scaled(1280, 720)
pictureLabel.setPixmap(init_image)

layout = QVBoxLayout()
layout.addWidget(pictureLabel)

win.setLayout(layout)
win.show()
print("QWidget ok!")

width = 1280
height = 720

process1 = (
    ffmpeg
    .input("udp://192.165.53.18:24000")
    .output('pipe:', format='rawvideo', pix_fmt='rgb24',s='{}x{}'.format(width, height))
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

        temp_image = QImage(in_frame, width, height, QImage.Format_RGB888)
        temp_pixmap = QPixmap.fromImage(temp_image)
        pictureLabel.setPixmap(temp_pixmap)

thread.start_new_thread( extract_frame, (process1, ) )

sys.exit(mapp.exec_())

process1.wait()

