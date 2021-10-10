import os

from PIL import Image

from app import MIN_SIZE, PROFILE_PIC_NAME, APP_ROOT


def validate_image_size(input_image_path):
    image = Image.open(input_image_path)
    width, height = image.size
    image.close()
    if width < MIN_SIZE[0] or height < MIN_SIZE[1]:
        return False
    else:
        return True


def save_image(id, picture_file):
    picture_ext = f".{picture_file.filename.split('.')[-1]}"
    picture_name = f'{PROFILE_PIC_NAME}{str(id)}{picture_ext}'

    temp_path = os.path.join(APP_ROOT, 'static/temp_pics', picture_name)
    picture_file.save(temp_path)

    if validate_image_size(temp_path):
        picture_path = os.path.join(APP_ROOT, 'static/profile_pics',
                                    picture_name)  # Путь для картинки профиля (для отображения в профиле)
        original_image = Image.open(temp_path)
        original_image.save(picture_path)
        original_image.close()
    else:
        picture_name = None

    if os.path.isfile(temp_path):
        os.remove(temp_path)

    return picture_name
