# Файл для группы Interface - работа с изображениями
from PIL import Image, ImageOps

class ImageUtils:
    @staticmethod
    def prepare_display_image(image, max_size, bg_color="#1e1e1e", border_color="#444444"):
        image.thumbnail(max_size)
        background = Image.new("RGB", image.size, bg_color)
        background.paste(image, (0, 0), image if image.mode == "RGBA" else None)
        bordered = ImageOps.expand(background, border=2, fill=border_color)
        return bordered