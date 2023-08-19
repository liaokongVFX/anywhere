import markdown
from anywhere.utils import RESOURCES_PATH


with open(f'{RESOURCES_PATH}/css/code.css', encoding='utf-8') as f:
    style = f.read()


def markdown_to_html(text):
    html = markdown.markdown(text, extensions=['fenced_code', 'codehilite'])
    return f'<style>{style}</style>{html}'
