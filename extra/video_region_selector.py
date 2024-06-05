
# 该工具用于对视频进行选框，得到该区域的零点坐标、宽、高。保存在视频同级目录config.json中
# python video_region_selector.py ../temp/从设问中获取答题的要点_temp.mp4
# 通过utils.py中的函数，可以快速实现视频的切割
# 切割视频
# crop_video(input_file="./temp/1.mp4", output_file="./temp/crop_output.mp4", width=980, height=720, x=0, y=0)
# 循环切割视频，读取视频同级目录的config.json文件
# loop_crop_video(source_folder="./temp/source", output_folder="./temp/output")

import cv2
import json
import os
import sys

class VideoRegionSelector:
    def __init__(self, video_path):
        self.video_path = video_path
        self.start_point = None
        self.end_point = None
        self.drawing = False
        self.img = None

        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            raise ValueError("无法打开视频文件")

        ret, frame = self.cap.read()
        if not ret:
            raise ValueError("无法读取视频帧")

        self.img = frame.copy()
        cv2.imshow('Frame', self.img)
        cv2.setMouseCallback('Frame', self.on_mouse)

    def on_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.start_point = (x, y)
            self.drawing = True

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.end_point = (x, y)
                img_copy = self.img.copy()
                cv2.rectangle(img_copy, self.start_point, self.end_point, (0, 255, 0), 2)
                cv2.imshow('Frame', img_copy)

        elif event == cv2.EVENT_LBUTTONUP:
            self.end_point = (x, y)
            self.drawing = False
            self.save_coordinates()

    def save_coordinates(self):
        x0, y0 = self.start_point
        x1, y1 = self.end_point
        x_min, x_max = min(x0, x1), max(x0, x1)
        y_min, y_max = min(y0, y1), max(y0, y1)
        width = x_max - x_min
        height = y_max - y_min

        data = {
            "width": width,
            "height": height,
            "x": x_min,
            "y": y_min
        }

        video_dir = os.path.dirname(self.video_path)
        json_path = os.path.join(video_dir, 'config.json')

        with open(json_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        print(f"选框的零点坐标：({x_min}, {y_min})，宽：{width}，高：{height}")
        print(f"参数已保存到 {json_path}")

        cv2.rectangle(self.img, self.start_point, self.end_point, (0, 255, 0), 2)
        cv2.imshow('Frame', self.img)

    def run(self):
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        self.cap.release()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("请提供视频文件路径作为命令行参数")
        sys.exit(1)

    video_path = sys.argv[1]
    try:
        selector = VideoRegionSelector(video_path)
        selector.run()
    except Exception as e:
        print(str(e))
        sys.exit(1)


