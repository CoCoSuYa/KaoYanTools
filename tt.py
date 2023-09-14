import os
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

email_server = 'smtp.gmail.com'
manager_email = 'yuqi.xia@shanbay.com'
email_pass = 'mnmbeanemjqfffbs'


def send_email_with_attachments(subject, body, to_email, dir_path):
    smtp_server = email_server
    port = 587
    sender_email = manager_email
    sender_password = email_pass

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

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


# Send email with all files in the 'datas' directory as attachments
send_email_with_attachments(
    subject='数据处理结果',
    body='请下载数据附件，有问题找QA夏宇奇！',
    to_email='xueyuanbawang@gmail.com',
    dir_path='datas'
)
