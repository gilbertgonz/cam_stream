import base64
import cv2
import numpy as np
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import os

## TODO: 
# simple face detection
# 3d scan

def calibrate(video_path):
    '''
    reference: https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
    '''

    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((6*7,3), np.float32)
    objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)
    
    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.

    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
        ret, img = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (7,6), None)
    
        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)
    
            corners2 = cv2.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
            imgpoints.append(corners2)
    
            # Draw and display the corners
            cv2.drawChessboardCorners(img, (7,6), corners2, ret)

    cap.release()
    cv2.destroyAllWindows()

    # Calibrate camera
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    # print(f"{mtx = }")

    # Reproj error
    mean_error = 0
    for i in range(len(objpoints)):
        imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2)/len(imgpoints2)
        mean_error += error
    
    reproj_error = mean_error/len(objpoints)
    # print(f"total error: {reproj_error}")

    return mtx, reproj_error

def face_detect(video_path):
    '''
    reference: https://www.geeksforgeeks.org/opencv-python-program-face-detection/
    '''
    face_cascade = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')

    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
        ret, img = cap.read()
        if not ret:
            break

        # convert to gray scale of each frames
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detects faces of different sizes in the input image
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x,y,w,h) in faces:
            # To draw a rectangle in a face 
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,255,0),2) 

        # send image to frontend
        send_images(img)

    cap.release()
    cv2.destroyAllWindows()

@app.route('/stream_images')
def send_images(img):
    """
    convert image to base64 for sending to frontend
    """
    _, buffer = cv2.imencode('.jpg', img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')

    return jsonify(img_base64), 200  