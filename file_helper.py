import os
import json

def get_json_content(path: str)->object:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
    
def get_pdf_content(path: str)->bytes:
    with open(path, 'rb') as f:
        return f.read()
