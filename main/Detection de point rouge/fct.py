import cv2
import numpy as np

lo=np.array([95, 100, 50])
hi=np.array([105, 255, 255])
cap=cv2.VideoCapture(0)

while True:
    ret, frame=cap.read()
    image=cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask=cv2.inRange(image, lo, hi)
    image2=cv2.bitwise_and(frame, frame, mask=mask)
    cv2.imshow('Camera', frame)
    cv2.imshow('image2', image2)
    cv2.imshow('Mask', mask)
    if cv2.waitKey(1)==ord('q'):
        break
cap.release()
cv2.destroyAllWindows()