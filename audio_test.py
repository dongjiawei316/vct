# -*- coding: utf-8 -*-
import os, sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QIcon

from matplotlib import pyplot as plt
import ffmpeg
import numpy as np
import time
import _thread as thread
import threading

resname = 'resource/1.ts'
#resname = 'in.mp4'

def decode_audio(in_filename, **input_kwargs):
    try:
        process1 = (ffmpeg
            .input(in_filename, **input_kwargs)
            .output('pipe:', format='s16le', acodec='pcm_s16le', ac=1, ar='16k')
           # .overwrite_output()
            .run_async(pipe_stdout=True)
        )
    except ffmpeg.Error as e:
        print(e.stderr, file=sys.stderr)
        sys.exit(1)
    return process1

class myThread(threading.Thread):  # 继承父类threading.Thread
    def __init__(self, threadID, name, audio_data):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.audio_data = audio_data

    def run(self):  # 把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        print
        "Starting " + self.name
        while True:
            in_bytes = self.audio_data.stdout.read(16)
            if not in_bytes:
               break

            print(in_bytes)
        #in1 = ffmpeg.input(resname)
        #a1 = in1.audio
        #audio_data = a1.output('-', format='s16le', acodec='pcm_s16le', ac=1, ar='16k')
        #audio_data.run()

        print
        "Exiting " + self.name


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 300, 220)
        self.setWindowTitle('Icon')
        self.setWindowIcon(QIcon('loss_rate.png'))

        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()

    audio_data = decode_audio(resname)

    # 创建新线程
    thread1 = myThread(1, "Thread-1", audio_data)

    # 开启线程
    thread1.start()
   # os.system(r"ffplay.exe 1.ts -x 800 -y 600 ")

    sys.exit(app.exec_())