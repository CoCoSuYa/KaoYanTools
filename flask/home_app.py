import glob
import os
import re
from multiprocessing import Process
import sys
from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages

from HandleFile.handleFileData import handle_file_data

app = Flask(__name__, template_folder='../pages', static_folder='../pages/statics')
app.secret_key = 'some_secret'
sys.path.append("..")


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
                excel_file.save(os.path.join('../backup', filename))
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
                json_file.save(os.path.join('../backup', filename))
                flash('Cookie文件上传成功!')
                return redirect(request.url)

    if not os.path.exists('../backup/'):
        os.makedirs('../backup/')
    excel_files = glob.glob('../backup/*.xls*')
    json_files = glob.glob('../backup/*.json')

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
        save_path = os.path.join('../backup', filename)
        excel_file.save(save_path)

        # 保存数据文件路径信息
        with open('../backup/data_info', 'w') as data_info_file:
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
        save_path = os.path.join('../backup', filename)
        json_file.save(save_path)

        # 保存Cookie文件路径信息
        with open('../backup/cookie_info', 'w') as cookie_info_file:
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

    run_in_new_process(handle_file_data, email, "../datas")
    flash('请求提交成功，请等待几分钟后检查邮箱获取数据！')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
