import subprocess
import sys
import os
import uuid
from flask import Flask, request, send_file, jsonify, render_template_string
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# Ensure Pillow, Flask, and Flask-Cors are installed
subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "Flask", "Flask-Cors"])

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>RBXG File Upload</title>
      <style>
        body {
          font-family: 'Arial', sans-serif;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100vh;
          background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
          margin: 0;
        }
        h1 {
          color: #333;
          font-size: 2.5em;
          margin-bottom: 20px;
        }
        form {
          display: flex;
          flex-direction: column;
          align-items: center;
          background: #fff;
          padding: 20px;
          border-radius: 10px;
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        input[type="file"] {
          margin-bottom: 10px;
        }
        button {
          background-color: #4CAF50;
          color: white;
          padding: 10px 20px;
          border: none;
          border-radius: 5px;
          cursor: pointer;
          font-size: 16px;
          transition: background-color 0.3s, transform 0.3s;
          margin: 5px;
        }
        button:hover {
          background-color: #45a049;
          transform: scale(1.05);
        }
        progress {
          width: 100%;
          margin-top: 10px;
          height: 20px;
          border-radius: 5px;
          overflow: hidden;
        }
        progress::-webkit-progress-bar {
          background-color: #f3f3f3;
        }
        progress::-webkit-progress-value {
          background-color: #4CAF50;
          transition: width 0.3s;
        }
        p {
          margin-top: 10px;
          font-size: 16px;
        }
        .modal {
          display: none;
          position: fixed;
          z-index: 1;
          left: 0;
          top: 0;
          width: 100%;
          height: 100%;
          overflow: auto;
          background-color: rgba(0, 0, 0, 0.4);
          justify-content: center;
          align-items: center;
        }
        .modal-content {
          background-color: #fff;;
          padding: 20px;
          border-radius: 10px;
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
          text-align: center;
        }
        .modal-content button {
          margin-top: 10px;
        }
        .fade-out {
          animation: fadeOut 1s forwards;
        }
        @keyframes fadeOut {
          from { opacity: 1; }
          to { opacity: 0; }
        }
      </style>
    </head>
    <body>
      <h1>📤 RBXG File Upload</h1>
      <form id="uploadForm">
        <input type="file" id="fileInput" name="upfile" required>
        <button type="submit">Upload 🚀</button>
        <button type="button" id="sendToFBI">Send to FBI 🕵️‍♂️</button>
      </form>
      <progress id="progressBar" value="0" max="100"></progress>
      <p id="status"></p>

      <div id="myModal" class="modal">
        <div class="modal-content">
          <p id="modalText"></p>
          <button id="redirectButton" style="display:none;">Redirect to Link</button>
          <button id="copyButton" style="display:none;">Copy Link</button>
          <button id="closeButton" style="display:none;">Close</button>
        </div>
      </div>

      <script>
        document.getElementById('uploadForm').addEventListener('submit', function(event) {
          event.preventDefault();
          uploadFile(false);
        });

        document.getElementById('sendToFBI').addEventListener('click', function() {
          uploadFile(true);
        });

        function uploadFile(sendToFBI) {
          const fileInput = document.getElementById('fileInput');
          const file = fileInput.files[0];
          const formData = new FormData();
          formData.append('upfile', file);
          formData.append('sendToFBI', sendToFBI);

          const xhr = new XMLHttpRequest();
          xhr.open('POST', '/api/uploaded', true);

          xhr.upload.onprogress = function(event) {
            if (event.lengthComputable) {
              const percentComplete = (event.loaded / event.total) * 100;
              document.getElementById('progressBar').value = percentComplete;
              if (sendToFBI) {
                document.getElementById('status').innerText = `Uploading to FBI Servers: ${Math.round(percentComplete)}% complete 📊`;
              } else {
                document.getElementById('status').innerText = `Upload ${Math.round(percentComplete)}% complete 📊`;
              }
            }
          };

          xhr.onload = function() {
            if (xhr.status === 200) {
              document.getElementById('status').innerText = 'Upload complete! ✅';
              const response = JSON.parse(xhr.responseText);
              showModal(response.fileUrl, sendToFBI);
            } else {
              document.getElementById('status').innerText = 'Upload failed! ❌';
            }
          };

          xhr.send(formData);
        }

        function showModal(fileUrl, sendToFBI) {
          const modal = document.getElementById('myModal');
          const modalText = document.getElementById('modalText');
          const redirectButton = document.getElementById('redirectButton');
          const copyButton = document.getElementById('copyButton');
          const closeButton = document.getElementById('closeButton');

          if (sendToFBI) {
            modalText.innerText = 'File sent to the FBI.';
            closeButton.style.display = 'block';
            redirectButton.style.display = 'none';
            copyButton.style.display = 'none';
          } else {
            modalText.innerText = 'File uploaded successfully.';
            redirectButton.style.display = 'block';
            copyButton.style.display = 'block';
            closeButton.style.display = 'none';
          }

          redirectButton.onclick = function() {
            window.location.href = fileUrl;
          };
          copyButton.onclick = function() {
            navigator.clipboard.writeText(fileUrl).then(() => {
              alert('Link copied to clipboard!');
            });
          };
          closeButton.onclick = function() {
            modal.style.display = 'none';
          };

          modal.style.display = 'flex';
        }

        window.onclick = function(event) {
          const modal = document.getElementById('myModal');
          if (event.target == modal) {
            modal.style.display = 'none';
          }
        };
      </script>
    </body>
    </html>
    '''

@app.route('/api/uploaded', methods=['POST'])
def upload_file():
    if 'upfile' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['upfile']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    send_to_fbi = request.form.get('sendToFBI') == 'true'
    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1]
    random_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_FOLDER, random_filename)

    if send_to_fbi:
        image = Image.open(file)
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        draw.text((10, 10), 'Sent to the FBI', font=font, fill='black')
        image.save(file_path)
    else:
        file.save(file_path)

    file_url = f"{request.url_root}public/uploads/{random_filename}"
    return jsonify({'fileUrl': file_url})

@app.route('/public/uploads/<filename>', methods=['GET', 'DELETE'])
def uploaded_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if request.method == 'DELETE':
        if os.path.exists(file_path):
            os.remove(file_path)
            return '', 200
        else:
            return '', 404
    else:
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return '', 404

@app.route('/alluploads')
def all_uploads():
    page = int(request.args.get('page', 1))
    per_page = 50
    files = os.listdir(UPLOAD_FOLDER)
    files.sort(key=lambda x: os.path.getmtime(os.path.join(UPLOAD_FOLDER, x)), reverse=True)
    total_pages = (len(files) - 1) // per_page + 1
    paginated_files = files[(page - 1) * per_page:page * per_page]

    files_html = ""
    for filename in paginated_files:
        file_url = f"/public/uploads/{filename}"
        if filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif')):
            files_html += f'<div class="upload"><img src="{file_url}" style="max-width: 100%;"></div>'
        elif filename.lower().endswith(('mp4', 'webm', 'ogg')):
            files_html += f'<div class="upload"><video controls style="max-width: 100%;"><source src="{file_url}" type="video/mp4"></video></div>'
        elif filename.lower().endswith(('mp3', 'wav', 'ogg')):
            files_html += f'<div class="upload"><audio controls style="max-width: 100%;"><source src="{file_url}" type="audio/mpeg"></audio></div>'
        else:
            files_html += f'<div class="upload"><a href="{file_url}" download>{filename}</a></div>'

    pagination_html = ""
    for i in range(1, total_pages + 1):
        if i == page:
            pagination_html += f'<span>{i}</span> '
        else:
            pagination_html += f'<a href="/alluploads?page={i}">{i}</a> '

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>All Uploads</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          background: #f5f5f5;
          padding: 20px;
        }
        .upload {
          margin-bottom: 20px;
        }
        .pagination {
          margin-top: 20px;
        }
      </style>
    </head>
    <body>
      <h1>All Uploads</h1>
      <div>
        {{ files_html|safe }}
      </div>
      <div class="pagination">
        {{ pagination_html|safe }}
      </div>
    </body>
    </html>
    ''', files_html=files_html, pagination_html=pagination_html)

@app.route('/images/<image>')
def get_image(image):
    file_path = os.path.join(UPLOAD_FOLDER, image)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='image/png')
    else:
        return '', 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
