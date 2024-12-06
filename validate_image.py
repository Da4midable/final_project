#!usr/bin/python3

from flask import request
from PIL import Image
import io

def is_valid_image(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image_upload(file):
    if file is None:
        return False, "No image file provided."

    if file.filename == '':
        return False, "No file selected."

    if not is_valid_image(file.filename):
        return False, "Invalid file type. Only image files are allowed."

    if file.content_type not in ['image/png', 'image/jpeg', 'image/gif', 'image/bmp', 'image/webp']:
        return False, "Invalid MIME type. Allowed types are: png, jpeg, gif, bmp, webp."

    file_content = file.read()

    MAX_FILE_SIZE = 5 * 1024 * 1024
    if len(file_content) > MAX_FILE_SIZE:
        return False, "File is too large. Maximum allowed size is 5 MB."

    try:
        img = Image.open(io.BytesIO(file_content))
        img.verify()
    except Exception as e:
        return False, f"Invalid image file: {str(e)}"

    file.seek(0)
    return True, file