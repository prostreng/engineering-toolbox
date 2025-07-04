from flask import Flask, render_template, request, send_file
import os
import shutil
import zipfile
from werkzeug.utils import secure_filename
from pathlib import Path

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

patterns = ["3dbuild", "andwg-1", "ewdwg-l", "ewdwg-r", "rfdwg-", "swdwg-", "roofdwg.dxf", "roofdwg2.dxf", "wnddwg", "partdwg", "keydwg", "walllnr", "bom.out", "cost.out"]
extensions = [".dxf", ".out"]

def matches_pattern(filename):
    lower = filename.lower()
    for p in patterns:
        if lower.startswith(p.lower()) or lower == p.lower():
            return True
    return False

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/file-filter', methods=['GET', 'POST'])
def file_filter():
    if request.method == 'POST':
        shutil.rmtree(UPLOAD_FOLDER, ignore_errors=True)
        shutil.rmtree(OUTPUT_FOLDER, ignore_errors=True)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

        uploaded_file = request.files['zip_file']
        if uploaded_file.filename.endswith('.zip'):
            zip_path = os.path.join(UPLOAD_FOLDER, secure_filename(uploaded_file.filename))
            uploaded_file.save(zip_path)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(UPLOAD_FOLDER)

            copied = 0
            for root, dirs, files in os.walk(UPLOAD_FOLDER):
                for file in files:
                    if matches_pattern(file) and Path(file).suffix.lower() in extensions:
                        src_path = os.path.join(root, file)
                        dest_path = os.path.join(OUTPUT_FOLDER, file)
                        shutil.copy2(src_path, dest_path)
                        copied += 1

            shutil.make_archive("FilteredFiles", 'zip', OUTPUT_FOLDER)
            return render_template('file_filter.html', copied=copied, download=True)

    return render_template('file_filter.html')

@app.route('/download')
def download():
    return send_file("FilteredFiles.zip", as_attachment=True)

@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    result = None
    if request.method == 'POST':
        try:
            num1 = float(request.form.get('num1', 0))
            num2 = float(request.form.get('num2', 0))
            operation = request.form.get('operation', 'add')
            if operation == 'add':
                result = num1 + num2
            elif operation == 'subtract':
                result = num1 - num2
            elif operation == 'multiply':
                result = num1 * num2
            elif operation == 'divide' and num2 != 0:
                result = num1 / num2
            else:
                result = 'Error'
        except:
            result = 'Error'
    return render_template('calculator.html', result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
