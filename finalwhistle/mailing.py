from flask import render_template

from finalwhistle import mail
from flask_mail import Message


# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xi-email-support
def send_email(recipients, subject, html_body):
    msg = Message(subject, recipients=recipients)
    msg.html = html_body
    mail.send(msg)


def send_registration_email(email, token):
    msg = Message(subject='Welcome to The Final Whistle',
                  recipients=[email])
    msg.body = ''
    msg.html = render_template('email_verification.html', email=email, token=token)
    mail.send(msg)


def send_password_reset_email():
    pass