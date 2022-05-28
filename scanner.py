import RPi.GPIO as GPIO
from time import sleep
import datetime
from email.message import EmailMessage
import mimetypes
import smtplib
import subprocess
import tempfile
import configparser

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def get_credentials():
    config = configparser.ConfigParser()
    config.read('config.ini')

    return (config['General']['username'], config['General']['password'])

def scan_to_file(file_path):
    cmd = f"scanimage --format png -d 'pixma:04A9173A_E03077' --resolution 150 > {file_path}"
    subprocess.run(cmd, shell=True)

def send_file(file_path):
    # Set basic info
    message = EmailMessage()
    message['From'] = 'soklicd@gmail.com'
    message['To'] = 'soklicd@gmail.com, vanda.gabron@gmail.com'
    message['Subject'] = 'Nov skeniran dokument'

    body = 'Dokument poskeniran ob: ' + str(datetime.datetime.now())
    message.set_content(body)

    # Add attachement
    mime_type, _ = mimetypes.guess_type(file_path)
    mime_type, mime_subtype = mime_type.split('/')

    with open(file_path, 'rb') as file:
        message.add_attachment(file.read(),
            maintype=mime_type,
            subtype=mime_subtype,
            filename='scan.png')

    # Send via SMTP
    username, password = get_credentials()

    mail_server = smtplib.SMTP_SSL('smtp.gmail.com')
    mail_server.login(username, password)
    mail_server.send_message(message)
    mail_server.quit()

def button_pressed(channel):
    print("scan button pressed")
    with tempfile.NamedTemporaryFile(dir='/dev/shm/', suffix='.png') as fp:
        print(f'Created temp file {fp.name}')
        scan_to_file(fp.name)
        send_file(fp.name)

    print("file sent")

    # Workaround because the buton event triggered twice for some reason
    GPIO.remove_event_detect(17)
    GPIO.add_event_detect(17, GPIO.FALLING, callback=button_pressed, bouncetime=2000)

GPIO.add_event_detect(17, GPIO.FALLING, callback=button_pressed, bouncetime=2000)

while True:
    sleep(1)
