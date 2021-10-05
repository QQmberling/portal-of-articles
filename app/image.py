from PIL import Image

from app import MAIN_SIZE, OTHER_SIZE, MIN_SIZE


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
