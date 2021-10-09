import os

from PIL import Image

from app import MAIN_SIZE, OTHER_SIZE, MIN_SIZE, PROFILE_PIC_NAME, APP_ROOT


def scale_image(input_image_path, output_image_path, width=None, height=None, target=True):
    original_image = Image.open(input_image_path)
    w, h = original_image.size
    if width and height:
        max_size = (width, height)
    elif width:
        max_size = (width, h)
    elif height:
        max_size = (w, height)
    else:
        if target:  # if target == True: need scaled picture for profile. else: need scaled picture for other html's
            max_size = MAIN_SIZE
        else:
            max_size = OTHER_SIZE

    original_image.thumbnail(max_size, Image.ANTIALIAS)
    original_image.save(output_image_path)
    original_image.close()

    scaled_image = Image.open(output_image_path)
    scaled_image.close()


def get_image_width(input_image_path):
    image = Image.open(input_image_path)
    width, _ = image.size
    image.close()
    return width


def get_image_height(input_image_path):
    image = Image.open(input_image_path)
    _, height = image.size
    image.close()
    return height


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
        picture_path2 = os.path.join(APP_ROOT, 'static/other_profile_pics',
                                     picture_name)  # Путь для картинки профиля уменьшенной версии (для остального)

        scale_image(temp_path, picture_path, target=True)
        scale_image(temp_path, picture_path2, target=False)
    else:
        picture_name = None

    if os.path.isfile(temp_path):
        os.remove(temp_path)

    return picture_name
