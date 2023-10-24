import json
import os
import random
import re
import time
from datetime import datetime, timedelta
import chardet
import requests
from openpyxl.reader.excel import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.workbook import Workbook
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

data_info_path = os.environ.get('data_info_file_path')
cookie_info_path = os.environ.get('cookie_info_file_path')
data_dir = os.environ.get('datas_dir')
xhs_cookie = ""
pgy_cookie = ""
hide, collected, current_fans_num, current_nicker, start_of_week, end_of_week = 0, 0, 0, 0, 0, 0
headers = {"referer": "https://www.xiaohongshu.com/",
           "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "

                         "Chrome/114.0.0.0 Safari/537.36",
           "Accept": "application/json, text/plain, */*"}
email_server = 'smtp.gmail.com'
manager_email = 'yuqi.xia@shanbay.com'
email_pass = 'mnmbeanemjqfffbs'
email_subject = '数据处理结果'
email_body = '请下载数据附件，有问题找QA夏宇奇！'


def split_into_weeks(data_ids):
    """
        将数据按周分组
    :param data_ids:
    :return:
    """

    # 过滤掉空字符串或不完整的数据
    filtered_data_ids = [item for item in data_ids if item and isinstance(item, list) and len(item) > 1 and item[0]]

    print("filtered_data_ids:", filtered_data_ids)

    for data in filtered_data_ids:
        if data[0] == "None":
            filtered_data_ids.remove(data)

    # 按日期排序
    sorted_data_ids = sorted(filtered_data_ids, key=lambda x: datetime.strptime(x[0], "%Y-%m-%d"))

    print("sorted_data_ids", sorted_data_ids)

    sorted_date_objects = [(datetime.strptime(date_str[0], "%Y-%m-%d").date(), date_str[1]) for date_str in
                           sorted_data_ids]

    chunks = []
    current_sublist = [sorted_date_objects[0]]
    week_end_date = current_sublist[0][0] + timedelta(
        days=(6 - current_sublist[0][0].weekday()))  # Calculate the end of the week for the first date

    for date_obj, date_id in sorted_date_objects[1:]:
        if date_obj <= week_end_date:
            current_sublist.append((date_obj, date_id))
        else:
            chunks.append(current_sublist)
            current_sublist = [(date_obj, date_id)]
            week_end_date = date_obj + timedelta(days=(6 - date_obj.weekday()))

    if current_sublist:  # Append any remaining dates
        chunks.append(current_sublist)
    return chunks


def write_data_excel_file(data_ids):
    """
        将帖子数据写入Excel文件
    :param data_ids:
    """
    wb = Workbook()
    ws = wb.active
    try:
        title_list = ["发布时间", "昵称", "博主等级", "笔记标题/链接", "笔记形式", "互动量", "点赞数", "收藏数",
                      "评论数", "爆文情况", "备注"]

        # 填写标题
        for title in title_list:
            ws.cell(row=1, column=title_list.index(title) + 1, value=title)

        # 填写数据
        for row in range(len(data_ids)):
            row += 2
            for col in range(12):
                col += 1
                if data_ids[row - 2] == "None":
                    ws.cell(row=row, column=col, value="")
                else:
                    if col == 5:
                        ws.cell(row=row, column=col - 1).hyperlink = data_ids[row - 2][col - 1]
                    elif col > 5:
                        ws.cell(row=row, column=col - 1, value=data_ids[row - 2][col - 1])
                    else:
                        ws.cell(row=row, column=col, value=data_ids[row - 2][col - 1])

    except Exception as e:
        print("Error:\n", "填写数据表时出错:", str(e))
    for col_num, col in enumerate(ws.columns, 1):
        max_length = 0
        for cell in col:
            try:
                # 增加对中文的处理，每个中文字符计为2个单位宽度
                cell_length = sum(2 if '\u4e00' <= ch <= '\u9fff' else 1 for ch in str(cell.value))
                if cell_length > max_length:
                    max_length = cell_length
            except Exception as e:
                print("Error:\n", "设置数据表列宽时发生错误:", str(e))
        adjusted_width = (max_length + 2)
        ws.column_dimensions[get_column_letter(col_num)].width = adjusted_width
    with open(data_info_path, 'rb') as f:
        rawdata = f.read()
        result = chardet.detect(rawdata)
        char_en = result['encoding']
    # 得到原文件名（不含扩展名）
    with open(data_info_path, "r", encoding=char_en) as file_path:
        file_url = file_path.read()
    filename_without_ext = os.path.splitext(os.path.basename(file_url))[0]
    # 构造新文件名（可以自行修改格式）
    new_filename = filename_without_ext + "_数据整理.xlsx"
    # 得到新文件的完整路径
    new_file_url = os.path.join(data_dir, new_filename)
    print(new_file_url)
    # 使用os.path.abspath确保路径是绝对的
    absolute_path = os.path.abspath(new_file_url)
    print(absolute_path)
    wb.save(absolute_path)


def write_date_excel_file(data_ids):
    """
        将排期数据按周写入Excel文件
    :param data_ids:
    """
    global start_of_week, end_of_week
    for data in data_ids:
        print(data)
        if any(date_obj[0] == "None" for date_obj in data):
            continue
        wb = Workbook()
        ws = wb.active
        try:
            # 填写标题
            days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            for idx, day in enumerate(days):
                ws.cell(row=1, column=idx + 1, value=day)

            # 计算那个周的周日
            start_of_week = data[0][0] - timedelta(days=data[0][0].weekday())
            # 计算那个周的周六
            end_of_week = data[-1][0] + timedelta(days=6 - data[-1][0].weekday())

            # 填写第二行的日期范围
            current_day = start_of_week
            col = 1
            while current_day <= end_of_week:
                ws.cell(row=2, column=col, value=current_day.strftime('%Y-%m-%d'))
                current_day += timedelta(days=1)
                col += 1
            # 根据日期写入ID
            for date_obj, date_id in data:
                row = 3
                while ws.cell(row=row, column=date_obj.weekday() + 1).value:
                    row += 1
                ws.cell(row=row, column=date_obj.weekday() + 1, value=date_id)
        except Exception as e:
            print("Error:\n", "填写排期表时出错:", str(e))

        for col_num, col in enumerate(ws.columns, 1):
            max_length = 0
            for cell in col:
                try:
                    # 增加对中文的处理，每个中文字符计为2个单位宽度
                    cell_length = sum(2 if '\u4e00' <= ch <= '\u9fff' else 1 for ch in str(cell.value))
                    if cell_length > max_length:
                        max_length = cell_length
                except Exception as e:
                    print("Error:\n", "设置排期表列宽时发生错误:", str(e))
            adjusted_width = (max_length + 2)
            ws.column_dimensions[get_column_letter(col_num)].width = adjusted_width
        with open(data_info_path, 'rb') as f:
            rawdata = f.read()
            result = chardet.detect(rawdata)
            char_en = result['encoding']
        # 得到原文件名（不含扩展名）
        with open(data_info_path, "r", encoding=char_en) as file_path:
            file_url = file_path.read()
        filename_without_ext = os.path.splitext(os.path.basename(file_url))[0]
        # 构造新文件名（可以自行修改格式）
        new_filename = filename_without_ext + f'_排期表{start_of_week}~{end_of_week}.xlsx'
        # 得到新文件的完整路径
        new_file_url = os.path.join(data_dir, new_filename)
        print(new_file_url)
        # 使用os.path.abspath确保路径是绝对的
        absolute_path = os.path.abspath(new_file_url)
        print(absolute_path)
        wb.save(absolute_path)


def write_up_fans_excel_file(data_ids):
    """
        将博主数据写入Excel文件
    :param data_ids:
    """
    wb = Workbook()
    ws = wb.active
    title1 = ["博主", "粉丝数", "备注"]
    ws.cell(1, 1, title1[0])
    ws.cell(1, 2, title1[1])
    ws.cell(1, 3, title1[2])
    row = 2
    for data in data_ids:
        ws.cell(row, 1, data[0])
        ws.cell(row, 2, data[1])
        ws.cell(row, 3, data[2])
        row += 1

    for col_num, col in enumerate(ws.columns, 1):
        max_length = 0
        for cell in col:
            try:
                # 增加对中文的处理，每个中文字符计为2个单位宽度
                cell_length = sum(2 if '\u4e00' <= ch <= '\u9fff' else 1 for ch in str(cell.value))
                if cell_length > max_length:
                    max_length = cell_length
            except Exception as e:
                print("Error:\n", "设置博主表列宽时发生错误：", str(e))

        adjusted_width = (max_length + 2)
        ws.column_dimensions[get_column_letter(col_num)].width = adjusted_width
    with open(data_info_path, 'rb') as f:
        rawdata = f.read()
        result = chardet.detect(rawdata)
        char_en = result['encoding']
    # # 得到文件名（不含扩展名）
    with open(data_info_path, "r", encoding=char_en) as file_path:
        file_url = file_path.read()
    filename_without_ext = os.path.splitext(os.path.basename(file_url))[0]
    # 构造新文件名（可以自行修改格式）
    new_filename = filename_without_ext + "_粉丝收集.xlsx"
    # 得到新文件的完整路径
    new_file_url = os.path.join(data_dir, new_filename)
    print(new_file_url)
    # 使用os.path.abspath确保路径是绝对的
    absolute_path = os.path.abspath(new_file_url)
    print(absolute_path)
    wb.save(absolute_path)


def load_excel_file():
    """
        读取Excel文件
    :return: 读取到的超链接列表
    """
    links = []
    with open(data_info_path, 'r') as data_path:
        path = data_path.read().strip()
    print("excel file path:", path)
    try:
        wb = load_workbook(filename=path)
        ws = wb.active
        for row in ws.iter_rows():
            for cell in row:
                link = cell.hyperlink.target if cell.hyperlink else None
                if link:
                    # 使用文件名作为键，并添加超链接到列表中
                    links.append(link)
                else:
                    links.append("")
    except Exception as e:
        print("Error:\n", "读取文件时出错:", str(e))
    return links


def load_json_file():
    """
        读取cookie文件
    """
    try:
        with open(cookie_info_path, 'r') as cookie_file_path:
            path = cookie_file_path.read().strip()
        print("cookie file path:", path)
        with open(path, 'r') as cookie_file:
            cookie_datas = json.load(cookie_file)
        global xhs_cookie, pgy_cookie
        xhs_cookie = cookie_datas['cookie1']
        pgy_cookie = cookie_datas['cookie2']
    except Exception as e:
        print(e)
        print("读取cookie文件时出错：cookie文件失效或缺失")


def get_redirected_url(url):
    """
        获取重定向后的url
    :param url: 原链接
    :return: 新链接
    """
    res = requests.get(url, headers=headers, cookies=xhs_cookie, allow_redirects=True)
    time.sleep(random.randint(1, 5))
    if res.history:  # 检查是否有重定向历史
        print(res.url)
        return res.url
    else:
        print(url)
        return url


def get_nicker_level(user_id):
    """
        获取博主等级
    :param user_id:
    """
    global current_fans_num, current_nicker
    url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
    res = requests.get(url, headers=headers, cookies=xhs_cookie)
    time.sleep(2)
    if res.status_code == 200:
        fans_pattern = r'<span class="count"[^>]*>([\d.]+[^\d\s]*)?</span><span class="shows"[^>]*>粉丝</span>'
        fans_match = re.search(fans_pattern, res.text)
        fans_num = fans_match.group(1)
        nicker_pattern = r'class="user-name"[^>]*>([^<]+)'
        nicker_match = re.search(nicker_pattern, res.text)
        current_nicker = nicker_match.group(1).strip()
        print("博主：", current_nicker, "粉丝数：", fans_num)
        if '万' not in fans_num:
            current_fans_num = int(fans_num)
            if 0 < int(fans_num) < 3000:
                return "新兴"
            elif 3000 <= int(fans_num) < 5000:
                return "普通"
            elif 5000 <= int(fans_num) < 10000:
                return "初级"
        else:
            current_fans_num = fans_num
            match = re.match(r"(\d+(\.\d+)?)", fans_num)
            fans_num = float(match.group(1))
            fans_num = int(fans_num * 10000)
            if 10000 <= fans_num < 50000:
                return "初级"
            elif 50000 <= fans_num < 500000:
                return "腰部"
            elif fans_num >= 500000:
                return "头部"
    else:
        return "博主已注销"


def get_note_ids_from_links(links):
    """
        从链接中获取用户id
    :param links: 链接列表
    """
    note_ids = []
    for link in links:
        try:
            if link == "":
                note_ids.append("None")
                print("第", links.index(link) + 1, "条帖子id:", "None")
            else:
                url = get_redirected_url(link)
                if "item" in url:
                    note_id = re.findall(r'item/(\w+)', url)[0]
                elif "website-login" in url:
                    if "item" in url:
                        note_id = re.findall(r'item%2F(\w+)', url)[0]
                    else:
                        note_id = re.findall(r'explore%2F(\w+)', url)[0]
                else:
                    note_id = re.findall(r'explore/(\w+)', url)[0]
                note_ids.append(note_id)
                print("第", links.index(link) + 1, "条帖子id:", note_id)
        except Exception as e:
            print("Error:\n", f" 第{links.index(link) + 1}条有问题,问题原因: {str(e)},将跳过该条")
            note_ids.append("None")
    return note_ids


def get_data(note_ids):
    """
        传入note_id获取帖子数据
    :param note_ids: 帖子id列表
    """
    global hide, collected
    data_ids = []
    for note_id in note_ids:
        if note_id == "None":
            data_ids.append("None")
            continue
        url = f"https://pgy.xiaohongshu.com/api/solar/note/{note_id}/detail?bizCode="
        res = requests.get(url, cookies=pgy_cookie)
        time.sleep(2)
        if res.status_code != 200:
            print(
                f"第{note_ids.index(note_id) + 1}条访问code{res.status_code},cookie2可能已过期，请获取蒲公英用户帖子detail接口的cookie"
                f"并替换掉cookies.json的cookie2")
            break
        else:
            data = json.loads(res.text)
            user_id = data["data"]["userId"]
            response = requests.get(
                f"https://pgy.xiaohongshu.com/api/solar/kol/dataV2/notesDetail?advertiseSwitch=1&orderType=1"
                f"&pageNumber=1"
                f"&pageSize=999&userId={user_id}&noteType=4", headers=headers, cookies=pgy_cookie)
            time.sleep(2)
            user_data = json.loads(response.text)
            if not user_data["data"]["list"]:
                collected = False
            else:
                collected = True
            note_link = data_fix(note_id, 5)
            remark = data_fix(note_link, 13)
            if collected:
                create_time = data_fix(data["data"]["createTime"], 1)
                nick_name = data_fix(data["data"]["userInfo"], 2)
                nick_level = data_fix(data["data"]["userInfo"], 3)
                if data["data"]["title"]:
                    note_title = data_fix(data["data"]["title"], 4)
                else:
                    note_title = data_fix(data["data"]["content"], 4)
                note_type = data_fix(data["data"]["videoInfo"], 6)
                read_num = data_fix(data["data"]["readNum"], 7)
                like_num = data_fix(data["data"]["likeNum"], 8)
                fav_num = data_fix(data["data"]["favNum"], 9)
                cmt_num = data_fix(data["data"]["cmtNum"], 10)
                interact_num = data_fix(data["data"], 11)
                interact_level = data_fix(interact_num, 12)
                print("第", note_ids.index(note_id) + 1, "条帖子数据获取成功")
                data_ids.append(
                    [create_time, nick_name, nick_level, note_title, note_link, note_type, read_num, interact_num,
                     like_num,
                     fav_num, cmt_num, interact_level, remark])
            elif collected is False and hide is False:
                create_time = data_fix(data["data"]["createTime"], 1)
                nick_name = data_fix(data["data"]["userInfo"], 2)
                nick_level = get_nicker_level(user_id)
                if data["data"]["title"]:
                    note_title = data_fix(data["data"]["title"], 4)
                else:
                    note_title = data_fix(data["data"]["content"], 4)
                note_type = data_fix(data["data"]["videoInfo"], 6)
                read_num = "None"
                interact_list = get_uncollected_note_data(note_id)
                interact_num = interact_list[0]
                like_num = interact_list[1]
                fav_num = interact_list[2]
                cmt_num = interact_list[3]
                interact_level = data_fix(interact_num, 12)
                remark = "帖子正常,但作者未被收录"
                print("第", note_ids.index(note_id) + 1, "条帖子数据获取成功")
                data_ids.append(
                    [create_time, nick_name, nick_level, note_title, note_link, note_type, read_num, interact_num,
                     like_num,
                     fav_num, cmt_num, interact_level, remark])
            elif collected is False and hide is True:
                create_time = "None"
                nick_name = "None"
                nick_level = "None"
                note_title = "None"
                note_type = "None"
                read_num = "None"
                interact_num = "None"
                like_num = "None"
                fav_num = "None"
                cmt_num = "None"
                interact_level = ""
                remark = "帖子已被隐藏且博主未被收录"
                print("第", note_ids.index(note_id) + 1, "条帖子数据获取成功")
                data_ids.append(
                    [create_time, nick_name, nick_level, note_title, note_link, note_type, read_num, interact_num,
                     like_num,
                     fav_num, cmt_num, interact_level, remark])
    return data_ids


def data_fix(data, data_type):
    """
        处理未经修复的数据
    :param data: 源数据
    :param data_type: 数据处理类型
    """
    global hide, current_fans_num
    if data_type == 1:
        if "今天" in data:
            fix_data = datetime.now().strftime('%Y-%m-%d')
        else:
            fix_data = data.split(" ")[0]
        return fix_data

    elif data_type == 2:
        if data["nickName"]:
            return data["nickName"]
        else:
            return "None"

    elif data_type == 3:
        current_fans_num = data["fansNum"]
        if 0 < data["fansNum"] < 3000:
            return "新兴"
        elif 3000 <= data["fansNum"] < 5000:
            return "普通"
        elif 5000 <= data["fansNum"] < 50000:
            return "初级"
        elif 50000 <= data["fansNum"] < 500000:
            return "腰部"
        elif data["fansNum"] >= 500000:
            return "头部"
        else:
            return "粉丝数异常”"

    elif data_type == 4:
        if len(data) > 30:
            return data[:30]
        else:
            return data

    elif data_type == 5:
        return f"https://www.xiaohongshu.com/explore/{data}"

    elif data_type == 6:
        if data:
            return "视频"
        else:
            return "图文"

    elif data_type == 7:
        return data

    elif data_type == 8:
        return data

    elif data_type == 9:
        return data

    elif data_type == 10:
        return data

    elif data_type == 11:
        return int(data["likeNum"]) + int(data["favNum"]) + int(data["cmtNum"])

    elif data_type == 12:
        if 0 <= data < 1000:
            return ""
        elif 1000 <= data < 5000:
            return "小爆文"
        elif 5000 <= data < 10000:
            return "中爆文"
        elif 10000 <= data:
            return "大爆文"
        else:
            return "互动量异常"

    elif data_type == 13:
        res = requests.get(data, headers=headers, cookies=xhs_cookie)
        time.sleep(2)
        if res.status_code == 200:
            hide = False
            return "帖子正常"
        elif res.status_code == 404:
            hide = True
            return "帖子已被删除"
        elif res.status_code == 423:
            hide = True
            return "帖子被隐藏"


def get_nicker_and_fans(links):
    """
        传入博主链接获取博主昵称和粉丝数
    :param links:
    """
    data_ids = []
    for link in links:
        print(link)
        try:
            user_id = re.search(r"profile/([^/?]+)", link).group(1)
        except AttributeError:
            data_ids.append(["None", "None", f"该链接有问题,链接位置{links.index(link) + 1}"])
            continue

        url = f"https://pgy.xiaohongshu.com/api/solar/kol/dataV2/notesDetail?advertiseSwitch=1&orderType=1&pageNumber" \
              f"=1&pageSize=999&userId={user_id}&noteType=4"
        response = requests.get(url, headers=headers, cookies=pgy_cookie)
        time.sleep(2)
        if response.status_code == 200:
            data_json = json.loads(response.text)
            if data_json["data"]["list"]:
                note_id = data_json["data"]["list"][0]["noteId"]
                url = f"https://pgy.xiaohongshu.com/api/solar/note/{note_id}/detail?bizCode="
                res = requests.get(url, cookies=pgy_cookie)
                time.sleep(2)
                data_json = json.loads(res.text)
                nick_name = data_fix(data_json["data"]["userInfo"], 2)
                data_fix(data_json["data"]["userInfo"], 3)
                fans_num = current_fans_num
                data_ids.append([nick_name, fans_num, "博主被蒲公英收录,取蒲公英具体数据"])
                print("list:", [nick_name, fans_num, "博主被蒲公英收录,取蒲公英具体数据"])
            else:
                get_nicker_level(user_id)
                data_ids.append([current_nicker, current_fans_num, "博主未被蒲公英收录，取博主主页粗数据"])
                print("profile:", [current_nicker, current_fans_num, "博主未被蒲公英收录，取博主主页粗数据"])

        else:
            print(
                f"第{links.index(link) + 1}条访问code{response.status_code},cookie2可能已过期，请获取蒲公英用户帖子detail接口的cookie"
                f"并替换掉cookies.json的cookie2")
            break
    return data_ids


# get_nicker_and_fans(["https://www.xiaohongshu.com/user/profile/62668fd2000000001000cb82"])

def get_uncollected_note_data(note_id):
    """
        获取未收录的笔记数据
    :param note_id:
    """
    res = requests.get(f"https://www.xiaohongshu.com/explore/{note_id}", headers=headers, cookies=xhs_cookie)
    time.sleep(2)
    if res.status_code != 200:
        print(
            f"note_id为{note_id}的访问code{res.status_code},cookie1可能已过期，请获取小红书用户登录me接口的cookie并替换掉cookies.json的cookie1")
    else:
        note_data = res.text
        pattern = r'interactInfo":({.*?})'
        match = re.search(pattern, note_data)
        json_data = json.loads(match.group(1))
        like_num = int(json_data["likedCount"])
        collect_num = int(json_data["collectedCount"])
        comment_num = int(json_data["commentCount"])
        interact_num = like_num + collect_num + comment_num
        return [interact_num, like_num, collect_num, comment_num]


def send_email_with_attachments(to_email, dir_path):
    smtp_server = email_server
    port = 587
    sender_email = manager_email
    sender_password = email_pass

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = email_subject
    msg.attach(MIMEText(email_body, 'plain'))

    # List all files in the directory
    files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]

    for file in files:
        file_path = os.path.join(dir_path, file)
        with open(file_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment',
                            filename=(Header(os.path.basename(file_path), 'utf-8').encode()))
            msg.attach(part)

    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
    print("邮件发送成功")


send_email_with_attachments("jiayu.li@shanbay.com", "../datas/")
def extract_text(text):
    pattern = r"(?<=window.__INITIAL_STATE__=).*(?=</script>)"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        result = match.group(0)
        end = result.find('</script>')  # find the first '</script>'
        if end != -1:
            result = result[:end].strip()
        return result
    else:
        return None


def get_nicker_level_by_user_id(user_id):
    """
            获取博主等级
        :param user_id:
    """
    url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
    res = requests.get(url, headers=headers, cookies=xhs_cookie)
    time.sleep(random.randint(1, 4))
    if res.status_code == 200:
        initial_state_str = extract_text(res.text)
        initial_state_str = initial_state_str.replace('undefined', '"undefined"')
        initial_state = json.loads(initial_state_str)
        nicker_datas = initial_state["user"]["userPageData"]['interactions']
        print(nicker_datas)
        for nicker_data in nicker_datas:
            if nicker_data["type"] == "fans":
                fans_num = nicker_data["count"]
                if 0 < int(fans_num) < 3000:
                    return "新兴"
                elif 3000 <= int(fans_num) < 5000:
                    return "普通"
                elif 5000 <= int(fans_num) < 50000:
                    return "初级"
                elif 50000 <= int(fans_num) < 500000:
                    return "腰部"
                elif int(fans_num) >= 500000:
                    return "头部"
    else:
        return "博主已注销"


def get_note_data(note_ids):
    data_ids = []
    for note_id in note_ids:
        success = False
        while not success:
            print("开始处理第", note_ids.index(note_id) + 1, "条数据")
            if note_id == "None":
                data_ids.append("None")
                print("链接", note_ids.index(note_id) + 1, "有问题,置为None")
                success = True
                continue
            res = requests.get(f"https://www.xiaohongshu.com/explore/{note_id}", headers=headers, cookies=xhs_cookie)
            if res.status_code == 200:
                try:
                    initial_state_str = extract_text(res.text)
                    initial_state_str = initial_state_str.replace('undefined', '"undefined"')
                    initial_state = json.loads(initial_state_str)
                    timestamp_ms = int(initial_state["note"]["noteDetailMap"][note_id]["note"]["time"])
                    timestamp_s = timestamp_ms / 1000  # Convert to seconds
                    date = datetime.fromtimestamp(timestamp_s)
                    formatted_date = date.strftime('%Y-%m-%d')
                    nicker_name = initial_state["note"]["noteDetailMap"][note_id]["note"]["user"]["nickname"]
                    nicker_id = initial_state["note"]["noteDetailMap"][note_id]["note"]["user"]["userId"]
                    time.sleep(random.randint(4, 6))
                    nicker_level = get_nicker_level_by_user_id(nicker_id)
                    if initial_state["note"]["noteDetailMap"][note_id]["note"]["title"] != "":
                        note_title = initial_state["note"]["noteDetailMap"][note_id]["note"]["title"]
                    else:
                        note_title = initial_state["note"]["noteDetailMap"][note_id]["note"]["desc"][0:30]
                    if initial_state["note"]["noteDetailMap"][note_id]["note"]["type"] == "video":
                        note_type = "视频"
                    else:
                        note_type = "图文"
                    print(initial_state["note"]["noteDetailMap"][note_id]["note"]["interactInfo"])
                    like_num = initial_state["note"]["noteDetailMap"][note_id]["note"]["interactInfo"]["likedCount"]
                    collect_num = initial_state["note"]["noteDetailMap"][note_id]["note"]["interactInfo"]["collectedCount"]
                    comment_num = initial_state["note"]["noteDetailMap"][note_id]["note"]["interactInfo"]["commentCount"]
                    interact_num = int(like_num) + int(collect_num) + int(comment_num)
                    if 0 <= interact_num < 1000:
                        note_level = ""
                    elif 1000 <= interact_num < 5000:
                        note_level = "小爆文"
                    elif 5000 <= interact_num < 10000:
                        note_level = "中爆文"
                    elif 10000 <= interact_num:
                        note_level = "大爆文"
                    else:
                        note_level = "互动量异常"
                    data_ids.append([formatted_date, nicker_name, nicker_level, note_title,
                                     f"https://www.xiaohongshu.com/explore/{note_id}", note_type, interact_num, like_num,
                                     collect_num, comment_num, note_level, "帖子正常"])
                    print([formatted_date, nicker_name, nicker_level, note_title,
                           f"https://www.xiaohongshu.com/explore/{note_id}", note_type, interact_num, like_num,
                           collect_num, comment_num, note_level, "帖子正常"])
                    print("第", note_ids.index(note_id) + 1, "条数据处理完成")
                    success = True
                except Exception as e:
                    print(e)
                    print("第", note_ids.index(note_id) + 1, "条数据处理失败,将重试")
            elif res.status_code == 404:
                data_ids.append(["", "", "", "", f"https://www.xiaohongshu.com/explore/{note_id}",
                                 "", "", "", "", "", "", "帖子已被删除"])
                print(["", "", "", "", f"https://www.xiaohongshu.com/explore/{note_id}",
                       "", "", "", "", "", "", "帖子已被删除"])
                print("第", note_ids.index(note_id) + 1, "条数据处理完成")
                success = True
            elif res.status_code == 403:
                data_ids.append(["", "", "", "", f"https://www.xiaohongshu.com/explore/{note_id}",
                                 "", "", "", "", "", "", "帖子已被隐藏"])
                print(["", "", "", "", f"https://www.xiaohongshu.com/explore/{note_id}",
                       "", "", "", "", "", "", "帖子已被隐藏"])
                print("第", note_ids.index(note_id) + 1, "条数据处理完成")
                success = True
            else:
                print("cookie失效,获取cookie后重试")
                success = True

    return data_ids
