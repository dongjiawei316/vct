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
import pyaudio

# udp://192.165.53.18:22000
#probe = ffmpeg.probe('resource/1.ts')

XShow_width = 800
XShow_height = 600
resname = 'resource/1.ts'
CHUNK = 1024

#显示界面类
class XShower(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        pictureLabel = QLabel()
        init_image = QPixmap("resource/cat.jpeg").scaled(XShow_width, XShow_height)
        pictureLabel.setPixmap(init_image)

        layout = QVBoxLayout()
        layout.addWidget(pictureLabel)

        self.pictureLabel = pictureLabel
        self.setLayout(layout)
        self.show()

def decode_stream(in_filename, **input_kwargs):
    try:
        stream_input=ffmpeg.input(in_filename, **input_kwargs)
        audio = stream_input.audio.output('pipe:', format='s16le', acodec='pcm_s16le', ac=1, ar='16k')
        video = stream_input.video.output('pipe:', format='rawvideo', pix_fmt='rgb24', s='{}x{}'.format(XShow_width, XShow_height))
        process1 = audio.run_async(pipe_stdout=True)
        process2 = video.run_async(pipe_stdout=True)

    except ffmpeg.Error as e:
        print(e.stderr, file=sys.stderr)
        sys.exit(1)
    return process1,process2

def extract_frame(win, process1):
    while True:

        in_bytes = process1.stdout.read(XShow_width * XShow_height * 3)
        if not in_bytes:
            break

        in_frame = (
            np
                .frombuffer(in_bytes, np.uint8)
                .reshape([XShow_height, XShow_width,3])
        )

        temp_image = QImage(in_frame, XShow_width, XShow_height, QImage.Format_RGB888)
        temp_pixmap = QPixmap.fromImage(temp_image)
        win.pictureLabel.setPixmap(temp_pixmap)

class myThread(threading.Thread):  # 继承父类threading.Thread
    def __init__(self, threadID, name, audio_data):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.audio_data = audio_data

    def run(self):  # 把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        print
        "Starting " + self.name
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        output=True)
        while True:
            in_bytes = self.audio_data.stdout.read(CHUNK)
            if not in_bytes:
               break
            stream.write(in_bytes)
        print
        "Exiting " + self.name

        # 停止数据流
        stream.stop_stream()
        stream.close()

        # 关闭 PyAudio
        p.terminate()

if __name__ == '__main__':
    mapp = QApplication(sys.argv)

    audio_data,video_data = decode_stream(resname)

    win = XShower()

    thread.start_new_thread( extract_frame, (win, video_data, ) )

    # 创建新线程
    thread1 = myThread(1, "Thread-1", audio_data)

    # 开启线程
    thread1.start()

sys.exit(mapp.exec_())



