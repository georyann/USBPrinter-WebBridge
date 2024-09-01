from flask import Flask, request, redirect, url_for, render_template, flash
import os
import platform
from datetime import datetime
import csv
import cups
import requests
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # 用于闪现消息
UPLOAD_FOLDER = 'uploads'
LOG_FOLDER = 'logs'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# 创建上传文件夹和日志文件夹
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def get_public_info():
    try:
        response = requests.get('https://ipinfo.io')
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"Error while getting public info: {e}")
        return None
def log_upload(file_name, client_ip, os_info):
    log_file = os.path.join(LOG_FOLDER, 'uploads_log.csv')
    with open(log_file, 'a', newline='') as csvfile:
        logwriter = csv.writer(csvfile)
        logwriter.writerow([datetime.now(), file_name, client_ip, os_info])
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            # 获取公网IP和操作系统信息
            public_info = get_public_info()
            client_ip = public_info.get('ip') if public_info else 'Unknown'
            os_info = public_info.get('org') if public_info else 'Unknown'
            # 记录上传信息
            log_upload(filename, client_ip, os_info)
            # 打印文件
            conn = cups.Connection()
            printers = conn.getPrinters()
            printer_name = list(printers.keys())[0]  # 使用第一个可用的打印机
            conn.printFile(printer_name, file_path, "Print Job", {})
            flash('File successfully uploaded and printed')
            return redirect(url_for('upload_file'))
    return render_template('index.html')
if __name__ == '__main__':
    app.run(debug=True)
