import os
import markdown


source_dir = os.path.dirname(__file__).replace('\\', '/')
with open(f'{source_dir}/resources/css/code.css', encoding='utf-8') as f:
    style = f.read()


def markdown_to_html(text):
    html = markdown.markdown(text, extensions=['fenced_code', 'codehilite'])
    return f'<style>{style}</style>{html}'
