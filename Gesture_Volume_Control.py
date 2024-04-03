import Hand_tracking_module as htm
import time
import cv2
import mediapipe as mp

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import math


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)

volume = cast(interface, POINTER(IAudioEndpointVolume))
volume_range = volume.GetVolumeRange()
min_volume = volume_range[0]
max_volume = volume_range[1]

def set_system_volume(volume_level):
    normalized_volume = volume_level / 100
    volume.SetMasterVolumeLevelScalar(normalized_volume, None)


win_name = 'Hand_Tracking'

cv2.namedWindow(win_name,cv2.WINDOW_NORMAL)
cap = cv2.VideoCapture(0)
detector = htm.handDetector()
    
pTime = 0
cTime = 0

while True:
    has_frame, frame = cap.read()
    if not has_frame:
        break
    frame, l1 = detector.DetectHand(frame)
    for cx,cy,id in l1:
        if id == 4 or id == 8:
            if id == 4:
                x4,y4 = cx,cy
            if id == 8:
                x8,y8 = cx,cy
            cv2.circle(frame,(cx,cy),3,(255,0,0),cv2.FILLED)
    if 'x4' in locals() and 'y4' in locals() and 'x8' in locals() and 'y8' in locals():
        # cv2.line(frame, (x4, y4), (x8, y8), (255, 0, 0), thickness=2)
        def vol():
            length = math.sqrt((x8 - x4) ** 2 + (y8 - y4) ** 2)
            if 0 <= length <= 100:
                return int(length)
            elif length < 0:
                return 0
            else:
                return 100
        set_system_volume(vol())

        rect_height = int(vol() * 2)
        cv2.rectangle(frame,(10,200),(30,400),color = (255,0,0),thickness = 2,lineType=cv2.FILLED)
        cv2.rectangle(frame, (10, 400 - rect_height), (30, 400), color=(255, 100, 0), thickness=cv2.FILLED)


    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    flipped_frame = cv2.flip(frame,1)
    cv2.putText(flipped_frame, f"FPS: {str(int(fps))}", (0,30),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,255),2)
    cv2.imshow(win_name,flipped_frame)
    key = cv2.waitKey(1)
    if key == 27:
        break


cap.release()
cv2.destroyWindow(win_name)
