from io import BytesIO

from django.conf import settings

from wand.image import Image
from PIL import Image as PILImage, ImageDraw
from PIL.Image import Resampling

from utils.constants import LA_LOC_TOP_LEFT, LA_LOC_BOTTOM_RIGHT, MAP_DOT_RADIUS, MAP_DOT_SHARPNESS


def generate_from_blob(blob):
    try:
        with Image(blob=blob, resolution=500) as pic:
            with pic.sequence[0] as first_page:
                with Image(first_page) as fp_img:
                    fp_img.sample(850, 1100)
                    return fp_img.make_blob('jpeg')
    except Exception:
        pass


def generate_dot_img(base_img_info, dot_location):
    img_width, img_height = base_img_info
    x, y = dot_location

    dot_image = PILImage.new(
        'RGBA',
        (img_width * MAP_DOT_SHARPNESS, img_height * MAP_DOT_SHARPNESS),
        (255, 255, 255, 0)
    )
    draw = ImageDraw.Draw(dot_image)

    upper_left_point = (MAP_DOT_SHARPNESS * (x - MAP_DOT_RADIUS), MAP_DOT_SHARPNESS * (y - MAP_DOT_RADIUS))
    bottom_right_point = (MAP_DOT_SHARPNESS * (x + MAP_DOT_RADIUS), MAP_DOT_SHARPNESS * (y + MAP_DOT_RADIUS))

    draw.ellipse([upper_left_point, bottom_right_point], fill='black')
    dot_image = dot_image.resize(base_img_info, Resampling.LANCZOS)

    return dot_image


def generate_map_thumbnail(longitude, latitude):
    if longitude < LA_LOC_TOP_LEFT[0] or longitude > LA_LOC_BOTTOM_RIGHT[0]:
        raise ValueError(f'Invalid longitude {longitude}')

    if latitude > LA_LOC_TOP_LEFT[1] or latitude < LA_LOC_BOTTOM_RIGHT[1]:
        raise ValueError(f'Invalid latitude {latitude}')

    with PILImage.open(f'{settings.BASE_DIR}/map.png') as base_image:
        img_width = base_image.width
        img_height = base_image.height

        x = (longitude - LA_LOC_TOP_LEFT[0]) / (LA_LOC_BOTTOM_RIGHT[0] - LA_LOC_TOP_LEFT[0]) * img_width
        y = (latitude - LA_LOC_TOP_LEFT[1]) / (LA_LOC_BOTTOM_RIGHT[1] - LA_LOC_TOP_LEFT[1]) * img_height

        dot_image = generate_dot_img(
            (img_width, img_height),
            (x, y)
        )

        image = PILImage.alpha_composite(base_image, dot_image)

        buf = BytesIO()
        image.save(buf, format='PNG')
        buffer_value = buf.getvalue()
        buf.close()

        return buffer_value
