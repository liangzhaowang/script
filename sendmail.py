# -*- coding: utf-8 -*-
import smtplib
import email.MIMEMultipart# import MIMEMultipart
import email.MIMEText# import MIMEText
import email.MIMEBase# import MIMEBase
import os.path
import mimetypes

From = "61852814@qq.com"
To = "liangzhaowang@aliyun.com"
file_name = "c:/DFSInfo.txt"

server = smtplib.SMTP("smtp.qq.com")
server.login("61852814","liang1031")

main_msg = email.MIMEMultipart.MIMEMultipart()
text_msg = email.MIMEText.MIMEText("this is a test text to text mime",_charset="utf-8")
main_msg.attach(text_msg)