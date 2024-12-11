from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from cv import calibrate

## TODO: 
# update frontend with real time images of cv process

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/app.js')
def javascript():
    return send_from_directory('.', 'app.js')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['upload']
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    mtx, reproj_error = calibrate(file_path)
    mtx_list = mtx.tolist()
    
    return jsonify({"message": "Calibration done", 
                    "matrix": mtx_list,
                    "reproj_error": reproj_error}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)#, ssl_context='adhoc')