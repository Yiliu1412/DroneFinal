import robomaster
from robomaster import config
from robomaster.robot import Drone
from robomaster.flight import Flight
from robomaster.camera import Camera
import cv2
import cv2.aruco
import time

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
aruco_params = cv2.aruco.DetectorParameters()
times = 3
camera_center = (640, 360)
config.LOCAL_IP_STR='192.168.10.2'
drone = Drone()
drone.initialize()
print(drone.get_drone_version())
print(drone.get_sn())
flight: Flight = drone.flight
camera: Camera = drone.camera
camera.start_video_stream(display = True)

flight.takeoff()
while True:
    image = camera.read_cv2_image(strategy = "newest")
    size = (1280, 720) # delete when using frame
    image = cv2.resize(image, size) # too
    corners, ids, rejected = cv2.aruco.detectMarkers(image, aruco_dict, parameters = aruco_params)
    cX, cY = (0, 0)
    topCenter = [0, 0]
    bottomCenter = [0, 0]

    if len(corners) > 0:
        ids = ids.flatten()
        for (markerCorner, markerID) in zip(corners, ids):
            # TOP-LEFT, TOP-RIGHT, BOTTOM-RIGHT, BOTTOM-LEFT
            if markerID != 10 :
                continue
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners
            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))
            # Draw margin
            # cv2.line(image, topLeft, topRight, (0, 255, 0), 2)
            # cv2.line(image, topRight, bottomRight, (0, 255, 0), 2)
            # cv2.line(image, bottomRight, bottomLeft, (0, 255, 0), 2)
            # cv2.line(image, bottomLeft, topLeft, (0, 255, 0), 2)
            # Draw ArUCo center (x, y)
            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)
            topCenter = ((topLeft[0] + topRight[0]) / 2, (topLeft[1] + topRight[1]) / 2)
            bottomCenter = ((bottomRight[0]+bottomLeft[0])/2, (bottomRight[1]+bottomLeft[1])/2)
            # print(cX, cY)
            # cv2.circle(image, (cX, cY), 4, (0, 0, 255), -1)
            # cv2.circle(image, (camera_center[0], camera_center[1]), 4, (0, 0, 255), -1)
            # # Mark ArUco ID
            # cv2.putText(image, str(markerID), (topLeft[0], topLeft[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            # print("[INFO] ArUco marker ID: {}".format(markerID))
            # cv2.imshow("Image", image)
            # cv2.waitKey(0)
            print('bottomCenter: {}, topCenter: {}'.format(bottomCenter[1], topCenter[1]))
            print('cX: {}, cY: {}\nheight: {}\n'.format(cX, cY, bottomCenter[1] - topCenter[1]))
            print("Objective: {} {}".format(cX, cY - times * (bottomCenter[1] - topCenter[1])))
            print((cX - camera_center[0]) ** 2 + (camera_center[1] - cY + times * (bottomCenter[1] - topCenter[1])) ** 2)

            if (cX - camera_center[0]) ** 2 + (camera_center[1] - cY + times * (bottomCenter[1] - topCenter[1])) ** 2 <= 10000:
                flight.rc(0, 10, 0)
                print('forward')

            else:
                flight.rc((cX - camera_center[0]) * 50 / 640, 0,
                            (camera_center[1] - cY + times * (bottomCenter[1] - topCenter[1])) * 50 / 360)
                # a:y b:z c:x
                print("calibrate")
            time.sleep(1)
flight.land()
