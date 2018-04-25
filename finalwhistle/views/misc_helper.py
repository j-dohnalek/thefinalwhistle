from flask import request
from html.parser import HTMLParser
from finalwhistle import db
from finalwhistle.models.contact import Message
import re


# https://stackoverflow.com/questions/753052
class MLStripper(HTMLParser):
    """
    Strip HTML from strings in Python
    """

    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def validate_contact_us():

    if request.method == 'POST':

        name = strip_tags(request.form['name'].strip())
        email = strip_tags(request.form['email'].strip())

        match = re.match(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)

        subject = strip_tags(request.form['subject'].strip())
        body = strip_tags(request.form['message'].strip())

        if len(name) < 2 or len(email) == 0 or len(subject) < 2 or len(body) < 2:
            return dict(error='All fields are required', success='')

        if match is None:
            return dict(error='Invalid email', success='')

        session = db.session
        new_message = Message(sender_name=name, sender_email=email, subject=subject, body=body)
        session.add(new_message)
        session.commit()

        return dict(error='', success='Message sent, thank you')

    return dict(error='', success='')
