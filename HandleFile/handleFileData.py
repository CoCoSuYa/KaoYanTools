from HandleFile.tools import load_excel_file, load_json_file, get_note_ids_from_links, write_data_excel_file, \
    split_into_weeks, write_date_excel_file, send_email_with_attachments, get_note_data


def handle_file_data(target_email, source_file):
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
    send_email_with_attachments(target_email, source_file)


def handle_file_nicker():
    pass
