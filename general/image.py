from PIL import Image

from general import AVATAR_SIZE_MAX, AVATAR_SIZE_MIN


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
            max_size = AVATAR_SIZE_MAX
        else:
            max_size = AVATAR_SIZE_MIN

    original_image.thumbnail(max_size, Image.ANTIALIAS)
    original_image.save(output_image_path)

    scaled_image = Image.open(output_image_path)
    scaled_image.close()


def get_image_size(input_image_path):
    image = Image.open(input_image_path)
    width, height = image.size
    image.close()
    return width, height
