import json
import json
import os
from multiprocessing import Process
from flask import request, redirect, url_for, flash, send_from_directory, Blueprint
from HandleFile.handleFileData import handle_file_data, handle_file_execute

pac_data_execute_blueprint = Blueprint('pac_data_execute', __name__)
file_path_url = os.getcwd() + "/backup/file_path.json"
with open(file_path_url) as file_path_json:
    file_path = json.load(file_path_json)
backup_dir = file_path['backup_dir']
datas_dir = file_path['datas_dir']
data_info_file_path = file_path['data_info_file_path']
cookie_info_file_path = file_path['cookie_info_file_path']


def run_in_new_process(func, *args):
    p = Process(target=func, args=args)
    p.start()
    return p


# Allowed file extensions
def allowed_excel(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['xls', 'xlsx']


def allowed_json(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['json']


@pac_data_execute_blueprint.route('/upload-excel', methods=['POST'])
def upload_excel():
    excel_file = request.files['excel_file']
    if excel_file.filename == '':
        flash('未选择文件')
        return redirect(url_for('index'))
    if excel_file and allowed_excel(excel_file.filename):
        filename = excel_file.filename
        save_path = os.path.join(backup_dir, filename)
        excel_file.save(save_path)
        print(save_path)
        # 保存数据文件路径信息
        with open(data_info_file_path, 'w') as data_info_file:
            data_info_file.write(save_path)

        flash('数据文件上传成功!')
    else:
        flash('上传失败，请确保文件类型为xls或xlsx!')
    return redirect(url_for('index'))


@pac_data_execute_blueprint.route('/upload-json', methods=['POST'])
def upload_json():
    json_file = request.files['json_file']
    if json_file.filename == '':
        flash('未选择文件')
        return redirect(url_for('index'))
    if json_file and allowed_json(json_file.filename):
        filename = json_file.filename
        save_path = os.path.join(backup_dir, filename)
        json_file.save(save_path)
        print(save_path)
        # 保存Cookie文件路径信息
        with open(cookie_info_file_path, 'w') as cookie_info_file:
            cookie_info_file.write(save_path)

        flash('Cookie文件上传成功!')
    else:
        flash('上传失败，请确保文件类型为json!')
    return redirect(url_for('index'))


@pac_data_execute_blueprint.route('/process-data', methods=['POST'])
def process_data():
    run_in_new_process(handle_file_data)
    flash('请求提交成功，请等待几分钟后检查文件列表下载数据！')
    return redirect(url_for('index'))


@pac_data_execute_blueprint.route('/data_list', methods=['GET'])
def data_list():
    # 获取文件路径列表
    files = [os.path.join(datas_dir, file) for file in os.listdir(datas_dir)]

    # 根据创建时间排序
    files.sort(key=os.path.getctime, reverse=True)  # 使用reverse=True来使得新创建的文件在上面

    # 从完整路径中获取文件名
    filenames = [os.path.basename(file) for file in files]

    file_list = "<ul>"
    for file in filenames:
        file_list += f"<li><a href='download/{file}'>{file}</a></li>"
    file_list += "</ul>"

    return file_list


@pac_data_execute_blueprint.route('/file_execute', methods=['POST'])
def file_execute():
    file = request.files['excel_file']
    if file.filename == '':
        flash('未选择文件')
        return redirect(url_for('index'))
    if file and allowed_excel(file.filename):
        filename = file.filename
        save_path = os.path.join(backup_dir, filename)
        file.save(save_path)
        print(save_path)
        flash('数据文件上传成功，马上开始处理，请稍后查看数据列表!')
        run_in_new_process(handle_file_execute, save_path, filename)
    else:
        flash('上传失败，请确保文件类型为xls或xlsx!')
    return redirect(url_for('index'))


@pac_data_execute_blueprint.route('/download/<filename>', methods=['GET'])
def download(filename):
    return send_from_directory(datas_dir, filename, as_attachment=True)