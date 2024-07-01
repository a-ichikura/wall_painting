## Detector for ArUco Markers with Intel RealSense Camera
## Author: zptang (UMass Amherst)

import time
import json
import numpy as np
import numpy
import cv2
from ArUcoDetector import ArUcoDetector
from pepper_video import Pepper
from TrajectoryTracker import TrajectoryTracker



def main():
    dict_to_use = "DICT_6X6_250"
    visualize = True
    grey_color = 153

    arucoDetector = ArUcoDetector(dict_to_use)
    tracker = TrajectoryTracker()

    pepper = Pepper()

    color_link = pepper.camera_device.subscribeCamera("Camera_Stream" + str(numpy.random.random()),1,1,13,30)
    depth_link = pepper.camera_device.subscribeCamera("Camera_Stream" + str(numpy.random.random()),2,1,11,30)
    if visualize: start_time = time.time()
    try:
        while True:
            color_raw = pepper.camera_device.getImageRemote(color_link)
            color_image = numpy.frombuffer(color_raw[6], numpy.uint8).reshape(color_raw[1], color_raw[0], 3)
            depth_raw = pepper.camera_device.getImageRemote(depth_link)
            depth_image = numpy.frombuffer(depth_raw[6], numpy.uint8).reshape(depth_raw[1], depth_raw[0], 3)

            # Remove unaligned part of the color_image to grey
            masked_color_image = np.where(depth_image <= 0, grey_color, color_image)

            # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

            # Detect markers and draw them on the images
            result = arucoDetector.detect(color_image)
            color_image = ArUcoDetector.getImageWithMarkers(color_image, result)
            masked_color_image = ArUcoDetector.getImageWithMarkers(masked_color_image, result)
            depth_colormap = ArUcoDetector.getImageWithMarkers(depth_colormap, result)

            # Update trajectory
            frame = depth_image
            tracker.updateTrajectory(frame, result)

            # Show images
            images = np.hstack((color_image, masked_color_image, depth_colormap))
            cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('RealSense', images)
            cv2.waitKey(1)

            if visualize:
                current_time = time.time()
                print(current_time-start_time)
                if current_time - start_time >= 20:
                    tracker.plotTrajectory()
                    tracker.clear()
                    start_time = current_time

    finally:
        pepper.camera_device.unsubscribe(color_link)
        pepper.camera_device.unsubscribe(depth_link)



if __name__ == '__main__':
    main()
