from flask import Flask, send_from_directory
from flask_socketio import SocketIO
import base64
import numpy as np
import cv2

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/app.js')
def javascript():
    return send_from_directory('.', 'app.js')

# WebSocket event for receiving image frames
@socketio.on('frame')
def handle_frame(data):
      print("test")
      # Remove the data URL prefix
      image_data = data.split(',')[1]
      # Decode base64 to numpy array
      nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
      # Decode image
      frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

      # Save the image frame
      cv2.imwrite('latest_frame.jpg', frame)
      print('Received frame of size:', frame.shape)

if __name__ == '__main__':
    # Run the server with SSL using adhoc
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)#, ssl_context='adhoc')
