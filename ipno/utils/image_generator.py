from wand.image import Image


def generate_from_blob(blob):
    try:
        with Image(blob=blob, resolution=500) as pic:
            with pic.sequence[0] as first_page:
                with Image(first_page) as fp_img:
                    fp_img.sample(850, 1100)
                    return fp_img.make_blob('jpeg')
    except Exception:
        pass
