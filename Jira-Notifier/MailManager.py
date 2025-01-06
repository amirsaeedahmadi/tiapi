# IMPORTING THE NECCESSARY PACKAGES

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from decouple import config
from datetime import datetime

# THE mail FUNCTON

def mail(to_user: str,subject: str,body: str) :

    # SETTING UP THE EMAIL HEADERS

    message = MIMEMultipart()
    message['From'] = config("MAIL_AUTH_USER")
    message['To'] = to_user
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    # SENDING THE EMAIL

    try:
        
        # CONNECTING TO THE SMTP SERVER AND AUTHENTICATING

        with smtplib.SMTP(config("SMTP_SERVER"), config("SMTP_PORT")) as server:
            server.starttls()  # UPGRADING THE CONNECTION TO SECURE
            server.login(config("MAIL_AUTH_USER"), config("MAIL_AUTH_PASSWORD"))

            # SENDING THE MESSAGE

            server.sendmail(message["From"], to_user, message.as_string())
            print(f"""Email To {message["To"]} With Subject ( {subject} ) Sent Successfully!""")

            # LOGGING THE EVENT

            with open('logs.txt','a') as logfile :
                logfile.write(f"""[ Mail Manager Log ]\nTIME = {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\nSENDER = {config("MAIL_AUTH_USER")}\nRECIPIENT = {to_user}\nSUBJECT = {subject}\n""")
                logfile.write(f"\n")

    except Exception as e:
        print(f"Failed To Send Email To {to_user}\n Reson :  {e}")
