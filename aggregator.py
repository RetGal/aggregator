#!/usr/bin/python3
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
    def __init__(self, file_name: str = None):
        config = configparser.RawConfigParser()
        config.read('aggregator.txt')

        try:
            props = dict(config.items('config'))
            if file_name:
                self.file_name = os.path.join(TARGET_PATH, file_name.strip('"').split(".")[0] + '.csv')
            else:
                self.file_name = os.path.join(TARGET_PATH, props['file_name'].strip('"').split(".")[0] + '.csv')
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
            new_name = '.'.join(parts[0], parts[1], str(number))
        os.rename(os.path.join(TARGET_PATH, file), os.path.join(TARGET_PATH, new_name))


def fetch_csv_content(csv_files: [str]):
    lines = []
    if NEW_YEAR and get_bot_type() == 'balancer':
        lines.append(read_csv_header(os.path.join(TARGET_PATH, csv_files[0])))
    for csv in csv_files:
        lines.append(read_csv(os.path.join(TARGET_PATH, csv)))
    return lines


def write_csv(file_content: str, filename_csv: str):
    with open(filename_csv, 'a') as file:
        file.write(file_content)


def read_csv(filename_csv: str):
    if os.path.isfile(filename_csv):
        with open(filename_csv, 'r') as file:
            return list(file)[-1]
    return None


def read_csv_header(filename_csv: str):
    if os.path.isfile(filename_csv):
        with open(filename_csv, 'r') as file:
            return list(file)[0]
    return None


def get_bot_type():
    bot_files = {
        'holdntrade': 'holdntrade.py',
        'maverage': 'maverage.py',
        'balancer': 'balancer.py'
    }
    for bot_type, file_name in bot_files.items():
        if os.path.isfile(os.path.join(TARGET_PATH, file_name)):
            return bot_type
    return 'unknown'


def send_mail(subject: str, text: str, attachment: str = None):
    recipients = ', '.join(CONF.recipient_addresses)
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
        part.add_header('Content-Disposition', "attachment; filename={}".format(os.path.basename(attachment)))
        msg.attach(part)

    server = smtplib.SMTP_SSL(CONF.mail_server, 465)
    # server.starttls()
    server.set_debuglevel(0)
    server.login(CONF.sender_address, CONF.sender_password)
    server.send_message(msg, None, None, mail_options=(), rcpt_options=())
    server.quit()


if __name__ == '__main__':
    print('Starting aggregator')

    if len(sys.argv) > 1:
        TARGET_PATH = sys.argv[1]
    else:
        TARGET_PATH = os.path.curdir

    if len(sys.argv) > 2:
        CONF = Config(sys.argv[2])
    else:
        CONF = Config()

    now = datetime.datetime.utcnow()
    if now.hour != 12:
        print('It is not past noon UTC: {}'.format(now.time().replace(microsecond=0)))
        sys.exit(0)

    NEW_YEAR = int(datetime.date.today().strftime("%j")) == 1

    if NEW_YEAR:
        archive_target_files()

    BOT_CSV_FILES = sorted(get_active_bot_csv_files())

    LINES = fetch_csv_content(BOT_CSV_FILES)

    CSV_CONTENT = ''.join([line for line in LINES if line is not None]) + '\n'

    write_csv(CSV_CONTENT, CONF.file_name)

    if CONF.send_emails:
        BOT_TYPE = get_bot_type()
        MAIL_CONTENT = BOT_TYPE + '@' + socket.gethostname()
        send_mail('Aggregator Report {}'.format(BOT_TYPE), MAIL_CONTENT, CONF.file_name)

    sys.exit(0)
