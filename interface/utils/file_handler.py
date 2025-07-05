# Файл для группы Interface - обработка файлов
import tkinter.filedialog as fd
from datetime import datetime
import os


class FileHandler:
    @staticmethod
    def open_image():
        return fd.askopenfilename(
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp")]
        )

    @staticmethod
    def save_musicxml(default_dir):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"music_notation_{timestamp}.musicxml"
        return fd.asksaveasfilename(
            initialdir=default_dir,
            initialfile=default_name,
            defaultextension=".musicxml",
            filetypes=[("MusicXML", "*.musicxml")]
        )