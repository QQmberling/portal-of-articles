import os
import uuid

from PIL import Image
from flask import current_app

from .exceptions import ValidationError


def delete_image(path):
    if os.path.isfile(path):
        os.remove(path)


def validate_image_size(path):
    with Image.open(path) as im:
        width, height = im.size
    if width < current_app.config['MIN_PICTURE_SIZE'][0] or height < current_app.config['MIN_PICTURE_SIZE'][1]:
        delete_image(path)
        raise ValidationError(
            f'({width}, {height}) is less than minimal size ({current_app.config["MIN_PICTURE_SIZE"][0]}, {current_app.config["MIN_PICTURE_SIZE"][1]})')


def convert_to_rgb(path):
    try:
        with Image.open(path) as im:
            image = im.convert('RGB')
            image.save(path)
    except:
        delete_image(path)
        raise ValidationError(f'Failed to convert to RGB')


def validate_image(picture_file):
    ext = picture_file.filename.split('.')[-1]
    if ext not in current_app.config['UPLOAD_EXTENSIONS']:
        raise ValidationError(f'Extension "{ext}" is not allowed')

    name = str(uuid.uuid4())
    name_dot_ext = f'{name}.{ext}'
    temp_path = os.path.join(current_app.root_path, 'static/temp_pics', name_dot_ext)
    picture_file.save(temp_path)
    convert_to_rgb(temp_path)
    validate_image_size(temp_path)
    return name_dot_ext, temp_path


def save_image(username, picture_file, old_picture_name):
    picture_name, temp_path = validate_image(picture_file)
    picture_path = os.path.join(current_app.root_path, f'static/profile_pics/{username}/',
                                picture_name)  # Путь для картинки профиля (для отображения в профиле)
    os.makedirs(os.path.dirname(picture_path), exist_ok=True)
    with Image.open(temp_path) as temp_image:
        temp_image.save(picture_path)
    if 'defaults/' not in old_picture_name:
        old_picture_path = os.path.join(current_app.root_path, 'static/profile_pics', old_picture_name)
        delete_image(old_picture_path)
    delete_image(temp_path)
    return picture_name, picture_file
