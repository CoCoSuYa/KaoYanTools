import html
import json
import os
import re
from datetime import datetime, timedelta

import requests
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.workbook import Workbook

from error_handler import handle_error

self_cookie1 = {
    "xhsTrackerId": "8ccb6590-a64e-4964-a02d-0fb4583a31ab",
    "xhsTrackerId.sig": "M4ymAnQxi3ng1zylgA9LGv-MTEOZHlR5WvERRQeVT7Y",
    "a1": "1878ec72b9f34xctibh4293i0ldcu98o6p98f8hlz50000155385",
    "webId": "eb8478acc157b0fd9a5276ca49d7d6cd",
    "gid": "yYWYdSWJiDK2yYWYdSWJDUYxjiq4CS93Dx4Jj1ujq381fY28S7jYli888y22qY288SqYD4df",
    "galaxy_creator_session_id": "EVByAGy7ls7O8RzKNxJH1B6IHM7TBnXHYI42",
    "galaxy.creator.beaker.session.id": "1691650713488097531969",
    "customerBeakerSessionId": "97266b672a8917fe7c49b13972272b40bf0e5ac9gAJ9cQAoWBAAAABjdXN0b21lclVzZXJUeXBlcQFLAlgOAAAAX2NyZWF0aW9uX3RpbWVxAkdB2TUish2hy1gJAAAAYXV0aFRva2VucQNYQQAAADEwODJhNzVjOTA3NjQ0YmFhNWY2YTY5NzE3ODJkOThjLTI4ZjQyNDRhZjgwMDQ1MTE5NDI0N2VkYjkxOWI2OWI2cQRYAwAAAF9pZHEFWCAAAABhYzhkYWUxZjAzMDk0NjAzOTY0NmNlZjU2M2VhMTk0M3EGWA4AAABfYWNjZXNzZWRfdGltZXEHR0HZNSKyHaHLWAYAAAB1c2VySWRxCFgYAAAANjEzMWRlNTgxOTE0NWEwMDAxZmQzZWE3cQlYAwAAAHNpZHEKWBgAAAA2NGQ0OGFjODY0MDAwMDAwMDAwMDAwMWZxC3Uu",
    "customerClientId": "367375640977445",
    "customer-sso-sid": "64d48ac8640000000000001f",
    "x-user-id-pgy.xiaohongshu.com": "6131d237000000001f03a57a",
    "solar.beaker.session.id": "1691650760555081230250",
    "access-token-pgy.xiaohongshu.com": "customer.ares.AT-d5af9c5ca69c44219eb09ee60ee1c449-2c98f9fcf1494ed98b0cef49ba6d686a",
    "access-token-pgy.beta.xiaohongshu.com": "customer.ares.AT-d5af9c5ca69c44219eb09ee60ee1c449-2c98f9fcf1494ed98b0cef49ba6d686a",
    "xsecappid": "xhs-pc-web",
    "abRequestId": "eb8478acc157b0fd9a5276ca49d7d6cd",
    "webBuild": "3.4.1",
    "websectiga": "3633fe24d49c7dd0eb923edc8205740f10fdb18b25d424d2a2322c6196d2a4ad",
    "sec_poison_id": "f65de8f0-5219-4414-a26e-14a5bb9a1e7a",
    "web_session": "040069b2d42fdaccfef0a92ee9364bb86e1968"
}
self_cookie2 = {
    "xhsTrackerId": "8ccb6590-a64e-4964-a02d-0fb4583a31ab",
    "xhsTrackerId.sig": "M4ymAnQxi3ng1zylgA9LGv-MTEOZHlR5WvERRQeVT7Y",
    "a1": "1878ec72b9f34xctibh4293i0ldcu98o6p98f8hlz50000155385",
    "webId": "eb8478acc157b0fd9a5276ca49d7d6cd",
    "gid": "yYWYdSWJiDK2yYWYdSWJDUYxjiq4CS93Dx4Jj1ujq381fY28S7jYli888y22qY288SqYD4df",
    "customerClientId": "367375640977445",
    "x-user-id-pgy.xiaohongshu.com": "6131d237000000001f03a57a",
    "abRequestId": "eb8478acc157b0fd9a5276ca49d7d6cd",
    "web_session": "040069b2d42fdaccfef0a92ee9364bb86e1968",
    "feratlin-status": "online",
    "feratlin-status.sig": "uBZJqsDDK9NbcHCALtzq7uIWcElHVIDWaGpKRyVXpts",
    "xsecappid": "xhs-pc-web",
    "webBuild": "3.4.1",
    "websectiga": "59d3ef1e60c4aa37a7df3c23467bd46d7f1da0b1918cf335ee7f2e9e52ac04cf",
    "customerBeakerSessionId": "69598bb45e1dcb3646c895d9a4237d6559cc4143gAJ9cQAoWBAAAABjdXN0b21lclVzZXJUeXBlcQFLAlgOAAAAX2NyZWF0aW9uX3RpbWVxAkdB2Tdx0LTdL1gJAAAAYXV0aFRva2VucQNYQQAAADEwODJhNzVjOTA3NjQ0YmFhNWY2YTY5NzE3ODJkOThjLTI4ZjQyNDRhZjgwMDQ1MTE5NDI0N2VkYjkxOWI2OWI2cQRYAwAAAF9pZHEFWCAAAAA5OTM5MWM5MTc4MjU0N2E4YTI3MDQyMzU1YTliNjA2N3EGWA4AAABfYWNjZXNzZWRfdGltZXEHR0HZN3HQtN0vWAYAAAB1c2VySWRxCFgYAAAANjEzMWRlNTgxOTE0NWEwMDAxZmQzZWE3cQlYAwAAAHNpZHEKWBgAAAA2NGRkYzc0MjY0MDAwMDAwMDAwMDAwMWFxC3Uu",
    "customer-sso-sid": "64ddc742640000000000001a",
    "solar.beaker.session.id": "1692256066993064610385",
    "access-token-pgy.xiaohongshu.com": "customer.ares.AT-6ab3ef556c594b4791e3a330aa0758b3-4606f83e37d6414d9efe98f784c4a1f0",
    "access-token-pgy.beta.xiaohongshu.com": "customer.ares.AT-6ab3ef556c594b4791e3a330aa0758b3-4606f83e37d6414d9efe98f784c4a1f0"
}
current_fans_num = 0
current_nicker = ""
path = None
hide, collected = False, False
start_of_week, end_of_week = None, None
headers = {"referer": "https://www.xiaohongshu.com/",
           "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "

                         "Chrome/114.0.0.0 Safari/537.36",
           "Accept": "application/json, text/plain, */*"}


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


def read_json_file(file_path):
    """
        读取cookie文件
    :param file_path:
    """
    try:
        with open(file_path, 'r') as f:
            global self_cookie1, self_cookie2
            cookie_datas = json.load(f)
            self_cookie1 = cookie_datas['cookie1']
            self_cookie2 = cookie_datas['cookie2']
    except Exception as e:
        print("读取cookie文件时出错：cookie失效或缺失")
        handle_error("读取cookie文件时出错：cookie失效或缺失")


def read_excel_file(file_paths):
    """
        读取Excel文件
    :param file_paths:
    :return:
    """
    links = []
    global path
    path = file_paths[0]
    for file_path in file_paths:
        ws = None
        try:
            wb = load_workbook(filename=file_path)
            ws = wb.active
        except Exception as e:
            print("Error:\n", "读取文件时出错:", str(e))
            handle_error(f"读取文件 {file_path}时出错: {str(e)}")

        for row in ws.iter_rows():
            for cell in row:
                try:
                    link = cell.hyperlink.target if cell.hyperlink else None
                    if link:
                        # 使用文件名作为键，并添加超链接到列表中
                        filename = os.path.basename(file_path)
                        links.append(link)
                    else:
                        links.append("")
                except Exception as e:
                    print("Error:\n", "读取文件链接时出错:", str(e))
                    handle_error(f"读取文件 {file_path}时出错: {str(e)}")

    return links


def write_data_excel_file(file_url, data_ids):
    """
        将帖子数据写入Excel文件
    :param file_url:
    :param data:
    """
    wb = Workbook()
    ws = wb.active
    try:
        title_list = ["发布时间", "昵称", "博主等级", "笔记标题/链接", "笔记形式", "阅读量", "互动量", "点赞数", "收藏数",
                      "评论数", "爆文情况", "备注"]

        # 填写标题
        for title in title_list:
            ws.cell(row=1, column=title_list.index(title) + 1, value=title)

        # 填写数据
        for row in range(len(data_ids)):
            row += 2
            for col in range(13):
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
        export_report(path, file_url, "填写数据时出错")
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
                export_report(path, file_url, "设置数据表列宽时发生错误")
        adjusted_width = (max_length + 2)
        ws.column_dimensions[get_column_letter(col_num)].width = adjusted_width
    # 得到原文件名（不含扩展名）
    filename_without_ext = os.path.splitext(os.path.basename(file_url))[0]
    # 得到文件所在目录
    dir_name = os.path.dirname(file_url)
    # 构造新文件名（可以自行修改格式）
    new_filename = filename_without_ext + "_数据整理.xlsx"
    # 得到新文件的完整路径
    new_file_url = os.path.join(dir_name, new_filename)
    print(new_file_url)
    wb.save(new_file_url)


def write_date_excel_file(file_url, data_ids):
    """
        将排期数据按周写入Excel文件
    :param file_url:
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
            export_report(path, file_url, "填写排期表时出错")

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
                    export_report(path, file_url, "整理排期表时设置列宽时出错")
            adjusted_width = (max_length + 2)
            ws.column_dimensions[get_column_letter(col_num)].width = adjusted_width

        # 得到原文件名（不含扩展名）
        filename_without_ext = os.path.splitext(os.path.basename(file_url))[0]
        # 得到文件所在目录
        dir_name = os.path.dirname(file_url)
        # 构造新文件名（可以自行修改格式）
        new_filename = filename_without_ext + f'_排期表{start_of_week}~{end_of_week}.xlsx'
        # 得到新文件的完整路径
        new_file_url = os.path.join(dir_name, new_filename)
        print(new_file_url)
        wb.save(new_file_url)


def write_up_fans_excel_file(file_url, data_ids):
    """
        将博主数据写入Excel文件
    :param file_url:
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

                export_report(path, file_url, "整理博主表时设置列宽时出错")
        adjusted_width = (max_length + 2)
        ws.column_dimensions[get_column_letter(col_num)].width = adjusted_width
    # # 得到文件名（不含扩展名）
    filename_without_ext = os.path.splitext(os.path.basename(file_url))[0]
    # 得到文件所在目录
    dir_name = os.path.dirname(file_url)
    # 构造新文件名（可以自行修改格式）
    new_filename = filename_without_ext + "_粉丝收集.xlsx"
    # 得到新文件的完整路径
    new_file_url = os.path.join(dir_name, new_filename)
    wb.save(new_file_url)


def export_report(reason, *args):
    """
        导出报错日志
    :param reason:
    :param args:
    """
    global path
    # 获取当前日期和时间
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 如果传入的是文件路径，获取其目录
    if os.path.isfile(path):
        file_path = os.path.dirname(path)

    # 创建日志文件路径
    log_path = os.path.join(file_path, "报错日志.txt")

    # 尝试写入或创建文件
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            for arg in args:
                if isinstance(arg, int):  # 如果是数字
                    f.write(f"{current_time}---第{arg}条链接异常,已自动跳过,原因:{reason}\n\n")
                elif isinstance(arg, str):  # 如果是文本
                    f.write(f"{current_time}---{arg},原因是{reason}\n\n")
    except Exception as e:
        print("Error:", "写入报错日志时发生错误:", str(e))
        handle_error(f"写入报错日志时发生错误:{str(e)}")


def get_redirected_url(url):
    """
        获取重定向后的url
    :param url: 原链接
    :return: 新链接
    """
    res = requests.get(url, headers=headers, cookies=self_cookie1, allow_redirects=True)

    if res.history:  # 检查是否有重定向历史
        return res.url
    else:
        return url


def get_nicker_level(user_id):
    """
        获取博主等级
    :param user_id:
    """
    global current_fans_num, current_nicker
    url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
    res = requests.get(url, headers=headers, cookies=self_cookie1)
    if res.status_code == 200:
        fans_pattern = r'<span class="count"[^>]*>([\d.]+[^\d\s]*)?</span><span class="shows"[^>]*>粉丝</span>'
        fans_match = re.search(fans_pattern, res.text)
        fans_num = fans_match.group(1)

        nicker_pattern = r'class="user-name"[^>]*>([^<]+)'
        nicker_match = re.search(nicker_pattern, res.text)
        current_nicker = nicker_match.group(1).strip()
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
            else:
                url = get_redirected_url(link)
                if "item" in url:
                    print(re.findall(r'item/(\w+)', url))
                    note_id = re.findall(r'item/(\w+)', url)[0]
                elif "website-login" in url:
                    if "item" in url:
                        print(re.findall(r'item%2F(\w+)', url))
                        note_id = re.findall(r'item%2F(\w+)', url)[0]
                    else:
                        print(re.findall(r'explore%2F(\w+)', url))
                        note_id = re.findall(r'explore%2F(\w+)', url)[0]
                else:
                    print(re.findall(r'explore/(\w+)', url))
                    note_id = re.findall(r'explore/(\w+)', url)[0]
                note_ids.append(note_id)
        except Exception as e:
            print("Error:\n", f" 第{links.index(link) + 1}条有问题,问题原因: {str(e)},将跳过该条")
            export_report(str(e), links.index(link) + 1)
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
        res = requests.get(url, cookies=self_cookie2)
        print(res.status_code, url)
        if res.status_code != 200:
            print(
                f"第{note_ids.index(note_id) + 1}条访问code{res.status_code},cookie2可能已过期，请获取蒲公英用户帖子detail接口的cookie并替换掉cookies.json的cookie2")
            handle_error(
                f"第{note_ids.index(note_id) + 1}条访问code{res.status_code},cookie2可能已过期，请获取蒲公英用户帖子detail接口的cookie并替换掉cookies.json的cookie2")
            break
        else:
            data = json.loads(res.text)
            user_id = data["data"]["userId"]
            response = requests.get(f"https://pgy.xiaohongshu.com/api/solar/kol/dataV2/notesDetail?advertiseSwitch=1&orderType=1&pageNumber=1"
                                    f"&pageSize=999&userId={user_id}&noteType=4", headers=headers, cookies=self_cookie2)
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
                data_ids.append([create_time, nick_name, nick_level, note_title, note_link, note_type, read_num, interact_num, like_num,
                                 fav_num, cmt_num, interact_level, remark])
            elif collected == False and hide == False:
                Ui_data = requests.get(note_link, headers=headers, cookies=self_cookie1)
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
                data_ids.append([create_time, nick_name, nick_level, note_title, note_link, note_type, read_num, interact_num, like_num,
                                 fav_num, cmt_num, interact_level, remark])
            elif collected == False and hide == True:
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
                remark = "k帖子已被隐藏且博主未被收录"
                data_ids.append([create_time, nick_name, nick_level, note_title, note_link, note_type, read_num, interact_num, like_num,
                                 fav_num, cmt_num, interact_level, remark])
    return data_ids


def data_fix(data, data_type):
    """
        处理未经修复的数据
    :param data: 源数据
    :param data_type: 数据处理类型
    """
    global hide, current_fans_num
    fix_data = None
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
        res = requests.get(data, headers=headers, cookies=self_cookie1)
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
        except Exception as e:
            export_report(str(e), links.index(link) + 1)
            data_ids.append(["None", "None", f"该链接有问题,链接位置{links.index(link) + 1}"])
            continue

        url = f"https://pgy.xiaohongshu.com/api/solar/kol/dataV2/notesDetail?advertiseSwitch=1&orderType=1&pageNumber=1&pageSize=999&userId={user_id}&noteType=4"
        response = requests.get(url, headers=headers, cookies=self_cookie2)
        if response.status_code == 200:
            data_json = json.loads(response.text)
            if data_json["data"]["list"]:
                note_id = data_json["data"]["list"][0]["noteId"]
                url = f"https://pgy.xiaohongshu.com/api/solar/note/{note_id}/detail?bizCode="
                res = requests.get(url, cookies=self_cookie2)
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
                f"第{links.index(link) + 1}条访问code{response.status_code},cookie2可能已过期，请获取蒲公英用户帖子detail接口的cookie并替换掉cookies.json的cookie2")
            handle_error(
                f"第{links.index(link) + 1}条访问code{response.status_code},cookie2可能已过期，请获取蒲公英用户帖子detail接口的cookie并替换掉cookies.json的cookie2")
            break
    return data_ids

# get_nicker_and_fans(["https://www.xiaohongshu.com/user/profile/62668fd2000000001000cb82"])

def get_uncollected_note_data(note_id):
    """
        获取未收录的笔记数据
    :param note_id:
    """
    res = requests.get(f"https://www.xiaohongshu.com/explore/{note_id}", headers=headers, cookies=self_cookie1)
    if res.status_code != 200:
        print(
            f"note_id为{note_id}的访问code{res.status_code},cookie1可能已过期，请获取小红书用户登录me接口的cookie并替换掉cookies.json的cookie1")
        handle_error(
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

