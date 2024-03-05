import glob
import json
import os
from flask import Flask, render_template, request, redirect, flash, get_flashed_messages

from flask_api.cmt_data_execute import cmt_data_execute_blueprint
from flask_api.pac_data_execute import pac_data_execute_blueprint

app = Flask(__name__, template_folder='../pages', static_folder='../pages/statics')
app.register_blueprint(cmt_data_execute_blueprint)
app.register_blueprint(pac_data_execute_blueprint)
app.secret_key = 'some_secret'

file_path_url = os.getcwd() + "/backup/file_path.json"
backup_dir = os.getcwd() + "/backup"
datas_dir = os.getcwd() + "/datas"
data_info_file_path = os.getcwd() + "/backup/data_info"
cookie_info_file_path = os.getcwd() + "/backup/cookie_info"
data = {
    "data_info_file_path": data_info_file_path,
    "cookie_info_file_path": cookie_info_file_path,
    "backup_dir": backup_dir,
    "datas_dir": datas_dir
}
# 写入 JSON 数据到文件
with open(file_path_url, 'w') as json_file:
    json.dump(data, json_file, indent=4)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle Excel file upload
        if 'excel_file' in request.files:
            excel_file = request.files['excel_file']
            if excel_file.filename == '':
                flash('未选择文件')
                return redirect(request.url)
            if excel_file and allowed_excel(excel_file.filename):
                filename = excel_file.filename
                excel_file.save(os.path.join(backup_dir, filename))
                print(os.path.join(backup_dir, filename))
                flash('数据文件上传成功!')
                return redirect(request.url)

        # Handle JSON file upload
        if 'json_file' in request.files:
            json_file = request.files['json_file']
            if json_file.filename == '':
                flash('未选择文件')
                return redirect(request.url)
            if json_file and allowed_json(json_file.filename):
                filename = json_file.filename
                json_file.save(os.path.join(backup_dir, filename))
                print(os.path.join(backup_dir, filename))
                flash('Cookie文件上传成功!')
                return redirect(request.url)

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    excel_files = glob.glob(os.path.join(backup_dir, '*.xls*'))
    json_files = glob.glob(os.path.join(backup_dir, '*.json'))

    has_excel = len(excel_files) > 0
    has_json = len(json_files) > 0

    return render_template('index.html', messages=get_flashed_messages(), has_excel=has_excel, has_json=has_json)


# Allowed file extensions
def allowed_excel(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['xls', 'xlsx']


def allowed_json(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['json']
