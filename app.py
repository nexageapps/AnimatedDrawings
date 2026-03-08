#!/usr/bin/env python
"""
Simple Web UI for Animated Drawings
Built on top of Facebook Research's AnimatedDrawings project
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
from pathlib import Path
from werkzeug.utils import secure_filename
import logging

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TEST_FOLDER'] = 'test_images'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['TEST_FOLDER'], exist_ok=True)

logging.basicConfig(level=logging.INFO)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test_images/<path:filename>')
def serve_test_image(filename):
    """Serve test images"""
    return send_file(os.path.join(app.config['TEST_FOLDER'], filename))

@app.route('/api/mode', methods=['GET'])
def get_mode():
    """Return current mode (testing or production)"""
    mode = os.environ.get('APP_MODE', 'testing')
    return jsonify({'mode': mode})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({
            'success': True,
            'filename': filename,
            'message': 'File uploaded successfully'
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/test-images', methods=['GET'])
def get_test_images():
    """Get list of test images"""
    test_images = []
    test_folder = Path(app.config['TEST_FOLDER'])
    
    for img_path in test_folder.glob('*.png'):
        test_images.append({
            'name': img_path.name,
            'path': str(img_path)
        })
    
    return jsonify({'images': test_images})

@app.route('/api/animate', methods=['POST'])
def animate_drawing():
    """Animate a drawing"""
    data = request.json
    image_path = data.get('image_path')
    motion = data.get('motion', 'dab')
    
    if not image_path:
        return jsonify({'error': 'No image path provided'}), 400
    
    # TODO: Implement animation logic using animated_drawings library
    # This will be integrated with the Facebook AnimatedDrawings code
    
    return jsonify({
        'success': True,
        'message': 'Animation started',
        'output': 'video.gif'
    })

if __name__ == '__main__':
    mode = os.environ.get('APP_MODE', 'testing')
    debug = mode == 'testing'
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Starting server in {mode.upper()} mode on port {port}")
    app.run(debug=debug, host='0.0.0.0', port=port)
