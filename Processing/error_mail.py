import smtplib
import traceback
import json
import constants as Const
from redis.exceptions import ConnectionError
from functools import partial
# Import the email modules we'll need
from email.mime.text import MIMEText
import time

def mail(message):
    me = 'loggingErrors@delphi.us'
    you = 'security@delphi.us'
    # Create a text/plain message
    msg = MIMEText(message)

    # me == the sender's email address
    # you == the recipient's email address
    msg['Subject'] = 'Logging Error'
    msg['From'] = me
    msg['To'] = you
    try:
        smtpObj = smtplib.SMTP('localhost')  
        smtpObj.sendmail(me, [you], msg.as_string())         
    except smtplib.SMTPException:
        print "Error: unable to send email"

    print message
    exit()

def generic_error(info):
    message = "Unexpected Error\n\n"
    message = message + "Machine info: " + json.dumps(info) + "\n"
    message = message + traceback.format_exc()
    mail(message)

def redis_func(func, info):
    for i in range(0,Const.RETRY_COUNT):
        try:
            return func()
        except (ConnectionError, AttributeError):
            if i < Const.RETRY_COUNT-1:
                time.sleep(Const.RETRY_WAIT)
                continue
            message = "Fatal Error: Unable to connect to Redis server at " + Const.REDIS_HOST + "\n\n"
            message = message + "Machine info: " + json.dumps(info) + "\n"
            message = message + traceback.format_exc()
            mail(message)
