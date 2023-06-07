import os
from email.mime.base import MIMEBase

import telebot
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders

TOKEN = '6212852313:AAFnr4L5vlQdZ7U78x0-ESTz4DTp_rd9x10'

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'pathtop33@gmail.com' # ЗАМЕНИТЬ
SENDER_PASSWORD = 'hcrmvvvnjwbsuuns' # ЗАМЕНИТЬ

bot = telebot.TeleBot(TOKEN)
attachments = []


@bot.message_handler(commands=['start'])
def send_welcome(message):
    cid = message.chat.id
    bot.send_message(cid, 'Привет! Я бот ЦЕНО для обратной связи. Введите команду /send, чтобы отправить письмо.')


@bot.message_handler(commands=['send'])
def send_email(message):
    cid = message.chat.id
    bot.send_message(cid, 'Введите тему письма:')
    bot.register_next_step_handler(message, send_subject)


def send_subject(message):
    cid = message.chat.id
    subject = message.text
    bot.send_message(cid, 'Введите текст письма:')
    bot.register_next_step_handler(message, send_message, subject)


def send_message(message,subject):
    cid = message.chat.id
    text = message.text

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = 'thelasthope158@gmail.com' # ЗАМЕНИТЬ
    msg['Subject'] = subject

    msg.attach(MIMEText(text, 'plain'))

    bot.send_message(cid, 'Прикрепите файлы (если необходимо), (1 файл в 1 сообщении) или отправьте письмо без вложений написав любое сообщение')
    bot.register_next_step_handler(message, attach_files, subject, msg)


def attach_files(message, subject, msg):
    cid = message.chat.id
    if message.content_type == 'document':
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path

        downloaded_file = bot.download_file(file_path)
        file_extension = os.path.splitext(message.document.file_name)[1]
        file_name = f'document{len(attachments) + 1}{file_extension}'
        attachments.append((file_name, downloaded_file))

    elif message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path

        downloaded_file = bot.download_file(file_path)
        file_extension = os.path.splitext(file_info.file_path)[1]
        file_name = f'photo{len(attachments) + 1}{file_extension}'
        attachments.append((file_name, downloaded_file))

    else:
        send_email_with_attachments(message, msg)
        return

    bot.send_message(cid,
                 'Прикрепите еще файлы (если необходимо), (1 файл в 1 сообщении) или напишите любое сообщение чтобы отправить письмо')
    bot.register_next_step_handler(message, attach_files, subject, msg)


def send_email_with_attachments(message, msg):
    cid = message.chat.id
    for file_name, file_data in attachments:
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(file_data)
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', f'attachment; filename="{file_name}"')
        msg.attach(attachment)

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        bot.send_message(cid, 'Письмо успешно отправлено. Ожидайте ответа.')
    except Exception as e:
        bot.send_message(cid, 'Ошибка при отправке письма, проверьте правильность введенной почты, попробуйте снова')
        print(e)

    attachments.clear()


bot.polling()
