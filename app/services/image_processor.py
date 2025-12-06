from io import BytesIO
from PIL import Image


def resize_image(data: bytes, max_width: int = 1080) -> bytes:
    img = Image.open(BytesIO(data)).convert("RGB")
    w, h = img.size
    if w > max_width:
        new_height = int(h * max_width / w)
        img = img.resize((max_width, new_height))
    out = BytesIO()
    img.save(out, format="JPEG", optimize=True, quality=85)
    return out.getvalue()


def create_thumbnail(data: bytes, size: tuple[int, int] = (200, 200)) -> bytes:
    img = Image.open(BytesIO(data)).convert("RGB")
    img.thumbnail(size)
    out = BytesIO()
    img.save(out, format="JPEG", optimize=True, quality=80)
    return out.getvalue()