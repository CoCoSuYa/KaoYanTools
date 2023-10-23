# import os
# import smtplib
# from email.header import Header
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from email.mime.base import MIMEBase
# from email import encoders
#
# email_server = 'smtp.gmail.com'
# manager_email = 'yuqi.xia@shanbay.com'
# email_pass = 'mnmbeanemjqfffbs'
#
#
# def send_email_with_attachments(subject, body, to_email, dir_path):
#     smtp_server = email_server
#     port = 587
#     sender_email = manager_email
#     sender_password = email_pass
#
#     msg = MIMEMultipart()
#     msg['From'] = sender_email
#     msg['To'] = to_email
#     msg['Subject'] = subject
#     msg.attach(MIMEText(body, 'plain'))
#
#     # List all files in the directory
#     files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
#
#     for file in files:
#         file_path = os.path.join(dir_path, file)
#         with open(file_path, 'rb') as f:
#             part = MIMEBase('application', 'octet-stream')
#             part.set_payload(f.read())
#             encoders.encode_base64(part)
#             part.add_header('Content-Disposition', 'attachment',
#                             filename=(Header(os.path.basename(file_path), 'utf-8').encode()))
#             msg.attach(part)
#
#     with smtplib.SMTP(smtp_server, port) as server:
#         server.starttls()
#         server.login(sender_email, sender_password)
#         server.sendmail(sender_email, to_email, msg.as_string())
#
#
# # Send email with all files in the 'datas' directory as attachments
# send_email_with_attachments(
#     subject='数据处理结果',
#     body='请下载数据附件，有问题找QA夏宇奇！',
#     to_email='xueyuanbawang@gmail.com',
#     dir_path='datas'
# )
import json
import re

import requests

from HandleFile.tools import load_excel_file, load_json_file, get_note_ids_from_links, get_data, write_data_excel_file, \
    split_into_weeks, write_date_excel_file, send_email_with_attachments

cookie_list = [
    {'domain': '.xiaohongshu.com', 'expiry': 1697340822, 'httpOnly': False, 'name': 'solar.beaker.session.id',
     'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '1696735870171025582833'},
    {'domain': '.xiaohongshu.com', 'httpOnly': False, 'name': 'unread', 'path': '/', 'sameSite': 'Lax', 'secure': False,
     'value': '{%22ub%22:%2264fab5fc000000001e032f2b%22%2C%22ue%22:%226517eee5000000001f035f43%22%2C%22uc%22:29}'},
    {'domain': 'www.xiaohongshu.com', 'httpOnly': False, 'name': 'cache_feeds', 'path': '/', 'sameSite': 'Lax',
     'secure': False, 'value': '[]'},
    {'domain': '.xiaohongshu.com', 'expiry': 1731296022, 'httpOnly': True, 'name': 'customer-sso-sid', 'path': '/',
     'sameSite': 'Lax', 'secure': False, 'value': '6522227e7500000000000003'},
    {'domain': '.xiaohongshu.com', 'expiry': 1697340822, 'httpOnly': True, 'name': 'customerBeakerSessionId',
     'path': '/', 'sameSite': 'Lax', 'secure': False,
     'value': '9381c9ca78630ae75267acd1f415d099597b04f5gAJ9cQAoWBAAAABjdXN0b21lclVzZXJUeXBlcQFLAlgOAAAAX2NyZWF0aW9uX3RpbWVxAkdB2UiIn4R64VgJAAAAYXV0aFRva2VucQNYQQAAADEwODJhNzVjOTA3NjQ0YmFhNWY2YTY5NzE3ODJkOThjLTI4ZjQyNDRhZjgwMDQ1MTE5NDI0N2VkYjkxOWI2OWI2cQRYAwAAAF9pZHEFWCAAAABkZWY4NmQzNTM3NDg0Y2M4OWVmNTA2NDZkYTE3YzUwOXEGWA4AAABfYWNjZXNzZWRfdGltZXEHR0HZSIifhHrhWAYAAAB1c2VySWRxCFgYAAAANjEzMWRlNTgxOTE0NWEwMDAxZmQzZWE3cQlYAwAAAHNpZHEKWBgAAAA2NTIyMjI3ZTc1MDAwMDAwMDAwMDAwMDNxC3Uu'},
    {'domain': '.xiaohongshu.com', 'expiry': 1728627947, 'httpOnly': False, 'name': 'xsecappid', 'path': '/',
     'sameSite': 'Lax', 'secure': False, 'value': 'xhs-pc-web'},
    {'domain': '.xiaohongshu.com', 'expiry': 1730345415, 'httpOnly': True, 'name': 'x-user-id-creator.xiaohongshu.com',
     'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '6131d237000000001f03a57a'},
    {'domain': 'www.xiaohongshu.com', 'expiry': 1726723444, 'httpOnly': False, 'name': 'b-user-id', 'path': '/',
     'sameSite': 'Lax', 'secure': False, 'value': '7b4e1ae6-3ff1-bf6a-3d20-83b84f0f3bc1'},
    {'domain': '.xiaohongshu.com', 'expiry': 1731296022, 'httpOnly': True, 'name': 'x-user-id-pgy.xiaohongshu.com',
     'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '6131d237000000001f03a57a'},
    {'domain': '.xiaohongshu.com', 'expiry': 1726210865, 'httpOnly': True, 'name': 'customerClientId', 'path': '/',
     'sameSite': 'Lax', 'secure': True, 'value': '367375640977445'},
    {'domain': '.xiaohongshu.com', 'expiry': 1697092546, 'httpOnly': False, 'name': 'sec_poison_id', 'path': '/',
     'sameSite': 'Lax', 'secure': False, 'value': 'ef410862-d285-4844-9517-a6176e57e790'},
    {'domain': '.xiaohongshu.com', 'expiry': 1713263630, 'httpOnly': True, 'name': 'gid.sign', 'path': '/',
     'sameSite': 'Lax', 'secure': False, 'value': 'oigtIKQ7eZyhKzMIintlC1uD5dc='},
    {'domain': '.xiaohongshu.com', 'expiry': 1697340822, 'httpOnly': False, 'name': 'access-token-pgy.xiaohongshu.com',
     'path': '/', 'sameSite': 'Lax', 'secure': False,
     'value': 'customer.ares.AT-9bacf60af3d04314829f7fd38ada00ba-3b183ed25b10494cbafbf828f063c0af'},
    {'domain': '.xiaohongshu.com', 'expiry': 1713263630, 'httpOnly': False, 'name': 'a1', 'path': '/',
     'sameSite': 'Lax', 'secure': False, 'value': '1878ec72b9f34xctibh4293i0ldcu98o6p98f8hlz50000155385'},
    {'domain': '.xiaohongshu.com', 'expiry': 1731651949, 'httpOnly': False, 'name': 'gid', 'path': '/',
     'sameSite': 'Lax', 'secure': False,
     'value': 'yYWYdSWJiDK2yYWYdSWJDUYxjiq4CS93Dx4Jj1ujq381fY28S7jYli888y22qY288SqYD4df'},
    {'domain': '.xiaohongshu.com', 'expiry': 1728628021, 'httpOnly': True, 'name': 'web_session', 'path': '/',
     'sameSite': 'Lax', 'secure': False, 'value': '040069b4704d235b6aa275d912374b15892aa2'},
    {'domain': '.xiaohongshu.com', 'expiry': 1697351141, 'httpOnly': False, 'name': 'websectiga', 'path': '/',
     'sameSite': 'Lax', 'secure': False, 'value': '2845367ec3848418062e761c09db7caf0e8b79d132ccdd1a4f8e64a11d0cac0d'},
    {'domain': '.xiaohongshu.com', 'expiry': 1723269424, 'httpOnly': False, 'name': 'abRequestId', 'path': '/',
     'sameSite': 'Lax', 'secure': False, 'value': 'eb8478acc157b0fd9a5276ca49d7d6cd'},
    {'domain': '.xiaohongshu.com', 'expiry': 1697340822, 'httpOnly': False,
     'name': 'access-token-pgy.beta.xiaohongshu.com', 'path': '/', 'sameSite': 'Lax', 'secure': False,
     'value': 'customer.ares.AT-9bacf60af3d04314829f7fd38ada00ba-3b183ed25b10494cbafbf828f063c0af'},
    {'domain': '.xiaohongshu.com', 'expiry': 1713263630, 'httpOnly': False, 'name': 'webId', 'path': '/',
     'sameSite': 'Lax', 'secure': False, 'value': 'eb8478acc157b0fd9a5276ca49d7d6cd'},
    {'domain': '.xiaohongshu.com', 'httpOnly': False, 'name': 'webBuild', 'path': '/', 'sameSite': 'Lax',
     'secure': False, 'value': '3.10.6'},
    {'domain': '.xiaohongshu.com', 'expiry': 1713263629, 'httpOnly': False, 'name': 'xhsTrackerId.sig', 'path': '/',
     'sameSite': 'Lax', 'secure': False, 'value': 'M4ymAnQxi3ng1zylgA9LGv-MTEOZHlR5WvERRQeVT7Y'},
    {'domain': '.xiaohongshu.com', 'expiry': 1713263629, 'httpOnly': False, 'name': 'xhsTrackerId', 'path': '/',
     'sameSite': 'Lax', 'secure': False, 'value': '8ccb6590-a64e-4964-a02d-0fb4583a31ab'}]
cookie_dict = {cookie["name"]: cookie["value"] for cookie in cookie_list}
print(cookie_dict)
headers = {"referer": "https://www.xiaohongshu.com/",
           "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "

                         "Chrome/114.0.0.0 Safari/537.36",
           "Accept": "application/json, text/plain, */*"}
cookie = cookie_dict
res = requests.get("https://www.xiaohongshu.com/user/profile/5d08d67000000000160217ed", headers=headers, cookies=cookie)
print(res.text)
note_data = res.text
initial_state = {}


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


initial_state_str = extract_text(res.text)
print(initial_state_str)
initial_state_str = initial_state_str.replace('undefined', '"undefined"')
data = json.loads(initial_state_str)
print(json.loads(initial_state_str))
nicker_datas = data["user"]["userPageData"]['interactions']
for nicker_data in nicker_datas:
    if nicker_data["type"] == "fans":
        fans_num = nicker_data["count"]
        if 0 < int(fans_num) < 3000:
            print("新兴")
        elif 3000 <= int(fans_num) < 5000:
            print("普通")
        elif 5000 <= int(fans_num) < 50000:
            print("初级")
        elif 50000 <= fans_num < 500000:
            print("腰部")
        elif fans_num >= 500000:
            print("头部")