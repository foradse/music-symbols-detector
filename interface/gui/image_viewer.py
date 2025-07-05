import os

import customtkinter as ctk
from PIL import Image, ImageOps


class ImageViewer:
    def __init__(self, parent):
        self.parent = parent
        self.image = None
        self.ctk_image = None

        self.create_widgets()

    def create_widgets(self):
        self.frame = ctk.CTkFrame(
            self.parent,
            fg_color="#1e1e1e",
            border_width=1,
            border_color="#444444",
            corner_radius=5
        )

        self.label = ctk.CTkLabel(
            self.frame,
            text="Изображение не загружено",
            text_color="#888888",
            fg_color="#1e1e1e"
        )
        self.label.pack(expand=True, fill="both", padx=10, pady=10)

        # Добавляем статусную строку
        self.status_label = ctk.CTkLabel(
            self.frame,
            text="Готов к загрузке",
            text_color="#aaaaaa",
            font=("Arial", 10)
        )
        self.status_label.pack(side="bottom", fill="x", padx=5, pady=5)

    def load_image(self, file_path):
        try:
            img = Image.open(file_path)
            img.thumbnail((600, 600))
            background = Image.new("RGB", img.size, "#1e1e1e")
            background.paste(img, (0, 0), img if img.mode == "RGBA" else None)

            self.ctk_image = ctk.CTkImage(
                light_image=background,
                dark_image=background,
                size=background.size
            )
            self.label.configure(image=self.ctk_image, text="")
            self.status_label.configure(text=f"Загружено: {os.path.basename(file_path)}")

        except Exception as e:
            self.label.configure(text=f"Ошибка загрузки: {str(e)}", image=None)
            self.status_label.configure(text="Ошибка загрузки изображения")
            raise e