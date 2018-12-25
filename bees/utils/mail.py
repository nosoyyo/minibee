import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from bees.utils.hub import ImageHub


def mailQRCode(uuid, status, qrcode):
    '''

    :param qrcode: generally anything that would be identified as picture
    '''
    print('mailQRCode called.')

    flag = True
    sender = os.environ.get('SENDER')
    pwd = os.environ.get('MAILPWD')
    print(f'uuid:{uuid} status:{status}')

    try:
        qrcode = ImageHub(qrcode)._mime
        print('qrcode loaded...')
        qrcode.add_header('Content-ID', '<qr-code>')
        msg = MIMEMultipart('related')
        msg['Subject'] = 'Scan your QR code! [Automatically sent by zworker]'
        msg['From'] = sender
        msg['To'] = sender
        text = MIMEText(f'<img src="cid:qr-code">', 'html', 'utf-8')
        msg.attach(text)
        msg.attach(qrcode)
        print('msg constructed.')

        server = smtplib.SMTP_SSL("smtp.qq.com", 465)
        login_info = server.login(sender, pwd)
        print(login_info)
        send_flag = server.sendmail(sender, [sender, ], msg.as_string())
        print(f'mail sent: {not bool(send_flag)}')
        server.quit()
    except Exception:
        flag = False
    return flag
