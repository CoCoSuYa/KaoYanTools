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



cookie_dict = {
    "xhsTrackerId": "8ccb6590-a64e-4964-a02d-0fb4583a31ab",
    "xhsTrackerId.sig": "M4ymAnQxi3ng1zylgA9LGv-MTEOZHlR5WvERRQeVT7Y",
    "a1": "1878ec72b9f34xctibh4293i0ldcu98o6p98f8hlz50000155385",
    "webId": "eb8478acc157b0fd9a5276ca49d7d6cd",
    "gid": "yYWYdSWJiDK2yYWYdSWJDUYxjiq4CS93Dx4Jj1ujq381fY28S7jYli888y22qY288SqYD4df",
    "customerClientId": "367375640977445",
    "x-user-id-pgy.xiaohongshu.com": "6131d237000000001f03a57a",
    "abRequestId": "eb8478acc157b0fd9a5276ca49d7d6cd",
    "b-user-id": "7b4e1ae6-3ff1-bf6a-3d20-83b84f0f3bc1",
    "x-user-id-creator.xiaohongshu.com": "6131d237000000001f03a57a",
    "web_session": "040069b4704d235b6aa275d912374b15892aa2",
    "customer-sso-sid": "65362f646400000000000005",
    "solar.beaker.session.id": "1698049892516067772803",
    "access-token-pgy.xiaohongshu.com": "customer.ares.AT-b736b11565664c8bba89080748585de4-9077b3b79f1948d1913de1aa0662547d",
    "access-token-pgy.beta.xiaohongshu.com": "customer.ares.AT-b736b11565664c8bba89080748585de4-9077b3b79f1948d1913de1aa0662547d",
    "xsecappid": "xhs-pc-web",
    "webBuild": "3.12.0",
    "websectiga": "82e85efc5500b609ac1166aaf086ff8aa4261153a448ef0be5b17417e4512f28",
    "sec_poison_id": "33de40a3-d9a2-4520-a845-710aff5e482c"
}
headers = {"referer": "https://www.xiaohongshu.com/",
           "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "

                         "Chrome/114.0.0.0 Safari/537.36",
           "Accept": "application/json, text/plain, */*"}
cookie = cookie_dict
res = requests.get("https://www.xiaohongshu.com/explore/653253d800000000250140e3?app_platform=android&app_version=8.8.0&author_share=1&ignoreEngage=true&share_from_user_hidden=true&type=normal&xhsshare=WeixinSession&appuid=5d8c7cb7000000000100244b&apptime=1698107534", headers=headers, cookies=cookie)
print(res.text)
# res = requests.get("https://www.xiaohongshu.com/user/profile/5d08d67000000000160217ed", headers=headers, cookies=cookie)
# print(res.text)
# note_data = res.text
# initial_state = {}
#
#
# def extract_text(text):
#     pattern = r"(?<=window.__INITIAL_STATE__=).*(?=</script>)"
#     match = re.search(pattern, text, re.DOTALL)
#     if match:
#         result = match.group(0)
#         end = result.find('</script>')  # find the first '</script>'
#         if end != -1:
#             result = result[:end].strip()
#         return result
#     else:
#         return None
#
#
# initial_state_str = extract_text(res.text)
# print(initial_state_str)
# initial_state_str = initial_state_str.replace('undefined', '"undefined"')
# data = json.loads(initial_state_str)
# print(json.loads(initial_state_str))
# nicker_datas = data["user"]["userPageData"]['interactions']
# for nicker_data in nicker_datas:
#     if nicker_data["type"] == "fans":
#         fans_num = nicker_data["count"]
#         if 0 < int(fans_num) < 3000:
#             print("新兴")
#         elif 3000 <= int(fans_num) < 5000:
#             print("普通")
#         elif 5000 <= int(fans_num) < 50000:
#             print("初级")
#         elif 50000 <= fans_num < 500000:
#             print("腰部")
#         elif fans_num >= 500000:
#             print("头部")