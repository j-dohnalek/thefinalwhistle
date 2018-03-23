# using sys module to inspect the name of the current method through the stack for testing purposes
import sys

def render_homepage():
    return sys._getframe(1).f_code.co_name


def render_login_form():
    return sys._getframe(1).f_code.co_name


def perform_user_login():
    return sys._getframe(1).f_code.co_name