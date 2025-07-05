import os
from PIL import Image

def load_image(image_path):
    """Загружает изображение и возвращает объект PIL.Image"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Файл не найден: {image_path}")
    return Image.open(image_path)

def save_image(image, path):
    """Сохраняет объект PIL.Image по указанному пути"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    image.save(path)

def list_images_in_folder(folder, exts=(".png", ".jpg", ".jpeg", ".JPG", ".JPEG")):
    """Возвращает список путей ко всем изображениям в папке"""
    return [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(exts)]

def clear_folder(folder):
    """Удаляет все файлы в папке (не удаляет саму папку)"""
    for f in os.listdir(folder):
        file_path = os.path.join(folder, f)
        if os.path.isfile(file_path):
            os.remove(file_path)

# Можно добавить функции для работы с PDF, если потребуется


if __name__ == "__main__":
    img = load_image("test.png")
    save_image(img, "output/test_copy.png")