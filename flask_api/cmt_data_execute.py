import json
import os
from multiprocessing import Process

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, get_flashed_messages
from HandleFile.handleFileData import handle_file_picture

file_path_url = os.getcwd() + "/backup/file_path.json"
with open(file_path_url) as file_path_json:
    file_path = json.load(file_path_json)
datas_dir = file_path['datas_dir']
backup_dir = file_path['backup_dir']
cmt_data_execute_blueprint = Blueprint('cmt_data_execute', __name__)


def run_in_new_process(func, *args):
    p = Process(target=func, args=args)
    p.start()
    return p


# Allowed file extensions
def allowed_csv(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['csv']


@cmt_data_execute_blueprint.route('/cmt_data_execute', methods=['GET'])
def cmt_data_execute():
    return render_template('cmt_data_execute.html', messages=get_flashed_messages())


@cmt_data_execute_blueprint.route('/upload-csv', methods=['POST'])
def upload_csv():
    csv_file = request.files['csv_file']
    if csv_file.filename == '':
        flash('未选择文件')
        return redirect(url_for('cmt_data_execute.cmt_data_execute'))
    if csv_file and allowed_csv(csv_file.filename):
        filename = csv_file.filename
        save_path = os.path.join(backup_dir, filename)
        csv_file.save(save_path)
        flash('数据文件上传成功，正在进行数据分析！')
        run_in_new_process(handle_file_picture, save_path)
    else:
        flash('上传失败，请确保文件格式为CSV')
    return redirect(url_for('cmt_data_execute.cmt_data_execute'))


@cmt_data_execute_blueprint.route('/data_list_cmt', methods=['GET'])
def data_list_cmt():
    files = [os.path.join(datas_dir, file) for file in os.listdir(datas_dir)]
    files.sort(key=os.path.getctime, reverse=True)
    filenames = [os.path.basename(file) for file in files]

    file_list = "<ul>"
    for file in filenames:
        file_list += f"<li><a href='download_cmt/{file}'>{file}</a></li>"
    file_list += "</ul>"

    return file_list


@cmt_data_execute_blueprint.route('/download_cmt/<filename>', methods=['GET'])
def download_cmt(filename):
    return send_from_directory(datas_dir, filename, as_attachment=True)
