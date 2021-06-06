from jinja2 import Template
from sanic.response import html, file

def render(path: str, **data):
    with open('template/files/{}'.format(path)) as f:
        template = Template(f.read())
    return html(template.render(**data))

def static(path: str):
    return file('template/static/{}'.format(path))