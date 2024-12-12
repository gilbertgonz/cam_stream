from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import base64
import cv2
import numpy as np

# from cv import calibrate, face_detect

## TODO: 
# update frontend with real time images of cv process

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Global vars
out_image = np.zeros((300, 300))
option = None

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/app.js')
def javascript():
    return send_from_directory('.', 'app.js')

@app.route('/option', methods=['POST'])
def get_option():
    global option
    option_tmp = request.data.decode('utf-8')
    option = option_tmp
        
    return jsonify({"message": "Done"}), 200
    
@app.route('/upload', methods=['POST'])
def upload_file():
    global option

    file = request.files['upload']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    if option == 'face':
        face_detect(file_path)
        return jsonify({"message": "Face detection done"}), 200
    if option == 'calibrate':
        mtx, reproj_error = calibrate(file_path)
        mtx_list = mtx.tolist()
        print(f"{mtx_list = }")
        
        return jsonify({"message": "Calibration done", 
                        "matrix": mtx_list,
                        "reproj_error": reproj_error}), 200

@app.route('/stream_images')
def send_images():
    """
    convert image to base64 for sending to frontend
    """
    global out_image
    _, buffer = cv2.imencode('.jpg', out_image)
    img_base64 = base64.b64encode(buffer).decode('utf-8')

    return jsonify(img_base64), 200 


######################## CV ########################
def calibrate(video_path):
    '''
    reference: https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
    '''
    global out_image

    board = (9,6)

    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((board[0]*board[1],3), np.float32)
    objp[:,:2] = np.mgrid[0:board[0],0:board[1]].T.reshape(-1,2)
    
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
        ret, corners = cv2.findChessboardCorners(gray, board, None)
    
        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)
    
            corners2 = cv2.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
            imgpoints.append(corners2)
    
            # Draw and display the corners
            out_image = img.copy()
            cv2.drawChessboardCorners(out_image, board, corners2, ret)
        
        # send image to frontend
        send_images()

    cap.release()
    print(f"{len(objpoints) = }")
    print(f"{len(imgpoints) = }")
    # Calibrate camera
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    print("hereeeeeeeeeeee2")

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
    global out_image

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
            out_image = img.copy()
            cv2.rectangle(out_image,(x,y),(x+w,y+h),(255,255,0),2) 

        # send image to frontend
        send_images()

    cap.release()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)#, ssl_context='adhoc')