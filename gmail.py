import settings
import smtplib


def send_mail(recipient_email, email_body):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(settings.gmail_user, settings.gmail_pass)

    # TODO change to real recipient email
    server.sendmail(settings.gmail_user, settings.gmail_user, email_body.encode('utf-8'))
    server.close()
