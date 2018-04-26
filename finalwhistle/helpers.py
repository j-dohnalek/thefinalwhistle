"""
Small miscellaneous functions which may be of use in various places
"""

def new_uuid():
    import uuid
    return str(uuid.uuid4())


def remove_html_tags(text):
    """
    Strip html tags from string, see [1]
    [1] https://tutorialedge.net/python/removing-html-from-string/
    :param text: string
    :return: input string stripped of html tags
    """
    import re
    rx = re.compile(r'<[^>]+>')
    return rx.sub('', text)