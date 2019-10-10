#!/usr/bin/python
import configparser
import datetime
import os
import smtplib
import socket
import sys
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Config:
    def __init__(self):
        config = configparser.RawConfigParser()
        config.read('aggregator.txt')

        try:
            props = dict(config.items('config'))
            self.file_name = TARGET_PATH + os.path.sep + props['file_name'].strip('"').split(".")[0] + '.csv'
            self.send_emails = bool(props['send_emails'].strip('"').lower() == 'true')
            self.recipient_addresses = props['recipient_addresses'].strip('"').replace(' ', '').split(",")
            self.sender_address = props['sender_address'].strip('"')
            self.sender_password = props['sender_password'].strip('"')
            self.mail_server = props['mail_server'].strip('"')
        except (configparser.NoSectionError, KeyError):
            raise SystemExit('Invalid configuration')


def get_active_bot_csv_files():
    return [fn.split(".")[0] + '.csv' for fn in os.listdir(TARGET_PATH) if fn.endswith('pid')]


def get_all_target_csv_files():
    needle = os.path.basename(CONF.file_name).split(".")[0]
    return [fn for fn in os.listdir(TARGET_PATH) if fn.startswith(needle)]


def archive_target_files():
    target_files = sorted(get_all_target_csv_files(), reverse=True)
    for file in target_files:
        if file.endswith('csv'):
            new_name = file + '.1'
        else:
            parts = file.split('.')
            number = int(parts[2])+1
            new_name = parts[0] + '.' + parts[1] + '.' + str(number)
        os.rename(TARGET_PATH + os.path.sep + file, TARGET_PATH + os.path.sep + new_name)


def fetch_csv_content(csv_files: [str]):
    lines = []
    for csv in csv_files:
        lines.append(read_csv(TARGET_PATH + os.path.sep + csv))
    return lines


def write_csv(file_content: str, filename_csv: str):
    with open(filename_csv, 'a') as file:
        file.write(file_content)


def read_csv(filename_csv: str):
    if os.path.isfile(filename_csv):
        with open(filename_csv, 'r') as file:
            return list(file)[-1]
    return None


def getBotType():
    if os.path.isfile(TARGET_PATH + os.path.sep + 'holdntrade.py'):
        return 'holdntrade'
    if os.path.isfile(TARGET_PATH + os.path.sep + 'maverage.py'):
        return 'maverage'
    return 'unknown'


def send_mail(subject: str, text: str, attachment: str = None):
    recipients = ", ".join(CONF.recipient_addresses)
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = CONF.sender_address
    msg['To'] = recipients

    readable_part = MIMEMultipart('alternative')
    readable_part.attach(MIMEText(text, 'plain', 'utf-8'))
    html = '<html><body><pre style="font:monospace">' + text + '</pre></body></html>'
    readable_part.attach(MIMEText(html, 'html', 'utf-8'))
    msg.attach(readable_part)

    if attachment and os.path.isfile(attachment):
        part = MIMEBase('application', 'octet-stream')
        with open(attachment, "rb") as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename={}".format(attachment))
        msg.attach(part)

    server = smtplib.SMTP(CONF.mail_server, 587)
    server.starttls()
    server.set_debuglevel(0)
    server.login(CONF.sender_address, CONF.sender_password)
    server.send_message(msg)
    server.quit()


if __name__ == '__main__':
    print('Starting aggregator')

    if len(sys.argv) > 1:
        TARGET_PATH = sys.argv[1]
    else:
        TARGET_PATH = os.path.curdir

    CONF = Config()

    if int(datetime.date.today().strftime("%j")) == 1:
        archive_target_files()

    BOT_CSV_FILES = sorted(get_active_bot_csv_files())

    LINES = fetch_csv_content(BOT_CSV_FILES)

    CSV_CONTENT = ''.join([line for line in LINES if line is not None])

    write_csv(CSV_CONTENT, CONF.file_name)

    if CONF.send_emails:
        MAIL_CONTENT = getBotType() + '@' + socket.gethostname()
        send_mail('Aggregator Report', MAIL_CONTENT, CONF.file_name)

    exit(0)
