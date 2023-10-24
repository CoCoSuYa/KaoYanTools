import glob
import os
import re
from multiprocessing import Process
from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages, send_from_directory
from HandleFile.handleFileData import handle_file_data

app = Flask(__name__, template_folder='../pages', static_folder='../pages/statics')
app.secret_key = 'some_secret'
base_dir = os.path.dirname(os.path.abspath(__file__))
backup_dir = os.path.join(base_dir, '../backup')
datas_dir = os.path.join(base_dir, '../datas')
data_info_file_path = os.path.join(backup_dir, 'data_info')
cookie_info_file_path = os.path.join(backup_dir, 'cookie_info')
os.environ["backup_dir"] = backup_dir
os.environ["datas_dir"] = datas_dir
os.environ["data_info_file_path"] = data_info_file_path
os.environ["cookie_info_file_path"] = cookie_info_file_path


def run_in_new_process(func, *args):
    p = Process(target=func, args=args)
    p.start()
    return p


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


@app.route('/upload-excel', methods=['POST'])
def upload_excel():
    excel_file = request.files['excel_file']
    if excel_file.filename == '':
        flash('未选择文件')
        return redirect(url_for('index'))
    if excel_file and allowed_excel(excel_file.filename):
        filename = excel_file.filename
        save_path = os.path.join(backup_dir, filename)
        excel_file.save(save_path)

        # 保存数据文件路径信息
        with open(data_info_file_path, 'w') as data_info_file:
            data_info_file.write(save_path)

        flash('数据文件上传成功!')
    else:
        flash('上传失败，请确保文件类型为xls或xlsx!')
    return redirect(url_for('index'))


@app.route('/upload-json', methods=['POST'])
def upload_json():
    json_file = request.files['json_file']
    if json_file.filename == '':
        flash('未选择文件')
        return redirect(url_for('index'))
    if json_file and allowed_json(json_file.filename):
        filename = json_file.filename
        save_path = os.path.join(backup_dir, filename)
        json_file.save(save_path)

        # 保存Cookie文件路径信息
        with open(cookie_info_file_path, 'w') as cookie_info_file:
            cookie_info_file.write(save_path)

        flash('Cookie文件上传成功!')
    else:
        flash('上传失败，请确保文件类型为json!')
    return redirect(url_for('index'))


@app.route('/process-data', methods=['POST'])
def process_data():
    email = request.form.get('emailInput', '').strip()
    print("target email:", email)

    # 正则表达式进行email格式验证
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        flash('请提供一个有效的电子邮件地址！')
        return redirect(url_for('index'))

    run_in_new_process(handle_file_data, email, datas_dir)
    flash('请求提交成功，请等待几分钟后检查邮箱获取数据！')
    return redirect(url_for('index'))


@app.route('/data_list', methods=['GET'])
def data_list():
    files = os.listdir(datas_dir)
    file_list = "<ul>"
    for file in files:
        file_list += f"<li><a href='download/{file}'>{file}</a></li>"
    file_list += "</ul>"
    return file_list


@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    return send_from_directory(datas_dir, filename, as_attachment=True)



