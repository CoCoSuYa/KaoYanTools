from HandleFile.financialDataProcess import load_file, write_file
from HandleFile.tools import load_excel_file, load_json_file, get_note_ids_from_links, write_data_excel_file, \
    split_into_weeks, write_date_excel_file, get_note_data, send_msg_to_DingTalk


def handle_file_data():
    self_url = load_excel_file()
    load_json_file()
    print("读取链接:", self_url)
    note_id_i = get_note_ids_from_links(self_url)
    print("读取笔记id:", note_id_i)
    j_data = get_note_data(note_id_i)
    print(j_data)
    nick_data_ids = []
    for i_data in j_data:
        # 取前两个元素
        if isinstance(i_data, list):
            nick_data_ids.append(i_data[:2])
        else:
            nick_data_ids.append(i_data)
    print(nick_data_ids)
    write_data_excel_file(j_data)
    weeks = split_into_weeks(nick_data_ids)
    print(weeks)
    write_date_excel_file(weeks)
    send_msg_to_DingTalk("数据处理完成！请相关人员去指定页面查看！")


def handle_file_nicker():
    pass


def handle_file_execute(file_url, file_name):
    print("开始处理文件！")
    data = load_file(file_url)
    write_file(data, file_name)
    print("文件处理完成！")

