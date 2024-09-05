from flask import Flask, request, redirect, url_for, render_template, flash
import os
import platform
from datetime import datetime
import csv
import cups
import requests
from PyPDF2 import PdfFileReader
from PIL import Image

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

# 检查文件扩展名是否在允许的类型中
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 获取公网 IP 信息
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

# 记录上传日志
def log_upload(file_name, client_ip, os_info):
    log_file = os.path.join(LOG_FOLDER, 'uploads_log.csv')
    with open(log_file, 'a', newline='') as csvfile:
        logwriter = csv.writer(csvfile)
        logwriter.writerow([datetime.now(), file_name, client_ip, os_info])

# 检测 PDF 文件的方向
def detect_orientation(file_path):
    try:
        with open(file_path, 'rb') as f:
            reader = PdfFileReader(f)
            page = reader.getPage(0)
            width = page.mediaBox.getWidth()
            height = page.mediaBox.getHeight()
            if width > height:
                return 3  # 横向
            else:
                return 4  # 纵向
    except Exception as e:
        print(f"Error while detecting orientation: {e}")
        return 4  # 默认纵向

# 处理图像文件，使其适应 A4 纸张但不拉伸
def process_image(file_path):
    try:
        with Image.open(file_path) as img:
            img_width, img_height = img.size
            paper_width, paper_height = 595, 842  # A4 size in points (72 points per inch)
            if img_width > paper_width or img_height > paper_height:
                img.thumbnail((paper_width, paper_height), Image.ANTIALIAS)
            new_img = Image.new('RGB', (paper_width, paper_height), (255, 255, 255))
            offset = ((paper_width - img.width) // 2, (paper_height - img.height) // 2)
            new_img.paste(img, offset)
            new_pdf_path = file_path.rsplit('.', 1)[0] + '_processed.pdf'
            new_img.save(new_pdf_path, 'PDF')
            return new_pdf_path
    except Exception as e:
        print(f"Error while processing image: {e}")
        return file_path

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # 检查请求中是否包含文件部分
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        files = request.files.getlist('file')
        if not files or all(file.filename == '' for file in files):
            flash('No selected file')
            return redirect(request.url)
        for file in files:
            if file and allowed_file(file.filename):
                filename = file.filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                # 获取公网 IP 和操作系统信息
                public_info = get_public_info()
                client_ip = public_info.get('ip') if public_info else 'Unknown'
                os_info = public_info.get('org') if public_info else 'Unknown'

                # 记录上传信息
                log_upload(filename, client_ip, os_info)

                # 连接到 CUPS 打印服务
                conn = cups.Connection()
                printers = conn.getPrinters()
                printer_name = list(printers.keys())[0]  # 使用第一个可用的打印机

                # 如果上传的是图像文件，处理图像文件
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    processed_file_path = process_image(file_path)
                else:
                    processed_file_path = file_path

                # 设置打印选项
                if processed_file_path.lower().endswith('.pdf'):
                    # 检测 PDF 文件的打印方向
                    orientation = detect_orientation(processed_file_path)
                    print_options = {
                        "media": "A4",  # 根据需要调整纸张尺寸
                        "orientation-requested": str(orientation),
                        "scaling": "100",  # 设置缩放比例为100%
                        "fit-to-page": "true",  # 适应页面
                        "number-up": "1",  # 每页一张
                        "number-up-layout": "lrtb"  # 从左到右，从上到下排列（横向）
                    }
                else:
                    print_options = {
                        "media": "A4",  # 根据需要调整纸张尺寸
                        "scaling": "100",  # 设置缩放比例为100%
                        "fit-to-page": "true",  # 适应页面
                        "number-up": "1",  # 每页一张
                        "number-up-layout": "lrtb"  # 从左到右，从上到下排列（横向）
                    }

                # 打印文件
                conn.printFile(printer_name, processed_file_path, "Print Job", print_options)
        flash('Files successfully uploaded and printed')
        return redirect(url_for('upload_file'))
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

