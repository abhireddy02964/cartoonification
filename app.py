from flask import Flask, render_template, request, send_file, redirect, url_for
import cv2
import numpy as np
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
OUTPUT_FOLDER = 'static/outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def cartoonify_image(img_path, output_path):
    img = cv2.imread(img_path)
    img = cv2.resize(img, (600, 600))
    
    # Convert to gray and apply median blur
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    
    # Detect edges
    edges = cv2.adaptiveThreshold(gray, 255,
                                  cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, 9, 9)
    
    # Apply bilateral filter to smoothen colors
    color = cv2.bilateralFilter(img, 9, 300, 300)
    
    # Combine edges and color
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    
    cv2.imwrite(output_path, cartoon)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['image']
        if file:
            filename = secure_filename(file.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
            file.save(upload_path)
            
            cartoonify_image(upload_path, output_path)
            
            return render_template('index.html', uploaded_image=url_for('static', filename=f'outputs/{filename}'))
    return render_template('index.html', uploaded_image=None)

@app.route('/download/<filename>')
def download_file(filename):
    path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)