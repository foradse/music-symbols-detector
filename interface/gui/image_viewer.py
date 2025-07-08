import os
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import gc


class ImageViewer:
    def __init__(self, parent):
        self.parent = parent
        self.tk_image = None
        self.pil_image = None
        self.is_destroyed = False  # Флаг для отслеживания состояния виджета

        self.create_widgets()

    def create_widgets(self):
        self.frame = ctk.CTkFrame(
            self.parent,
            fg_color="#1e1e1e",
            border_width=1,
            border_color="#444444",
            corner_radius=5
        )

        # Создаем стандартный Tkinter Label внутри CTkFrame
        self.label = tk.Label(
            self.frame,
            text="Изображение не загружено",
            fg="#888888",
            bg="#1e1e1e",
            compound="center"
        )
        self.label.pack(expand=True, fill="both", padx=10, pady=10)

        self.status_label = ctk.CTkLabel(
            self.frame,
            text="Готов к загрузке",
            text_color="#aaaaaa",
            font=("Arial", 10)
        )
        self.status_label.pack(side="bottom", fill="x", padx=5, pady=5)

    def load_image(self, file_path):
        if self.is_destroyed:
            return False

        try:
            # Очищаем предыдущее изображение
            self.clear_image()

            # Загружаем новое изображение
            self.pil_image = Image.open(file_path)

            # Масштабируем с сохранением пропорций
            width, height = self.pil_image.size
            max_size = 800
            if width > max_size or height > max_size:
                ratio = min(max_size / width, max_size / height)
                new_size = (int(width * ratio), int(height * ratio))
                self.pil_image = self.pil_image.resize(new_size, Image.Resampling.LANCZOS)

            # Конвертируем в Tkinter PhotoImage
            self.tk_image = ImageTk.PhotoImage(self.pil_image)

            # Отображаем изображение
            self.label.configure(image=self.tk_image, text="")
            self.status_label.configure(
                text=f"Загружено: {os.path.basename(file_path)}",
                text_color="#aaaaaa"
            )

            return True

        except Exception as e:
            if not self.is_destroyed:
                self.label.configure(
                    text=f"Ошибка загрузки: {str(e)}",
                    fg="#ff5555"
                )
                self.status_label.configure(
                    text=f"Ошибка загрузки: {str(e)}",
                    text_color="#ff5555"
                )
            return False

    def clear_image(self):
        """Безопасная очистка текущего изображения"""
        if self.is_destroyed:
            return

        try:
            # Удаляем изображение из виджета
            if self.label.winfo_exists():
                self.label.configure(image="", text="Изображение не загружено", fg="#888888")

            # Очищаем статус
            if self.status_label.winfo_exists():
                self.status_label.configure(text="Готов к загрузке", text_color="#aaaaaa")

            # Закрываем PIL Image
            if self.pil_image is not None:
                self.pil_image.close()
                self.pil_image = None

            # Очищаем ссылку на Tkinter image
            self.tk_image = None

            # Принудительный сбор мусора
            gc.collect()

        except Exception as e:
            # Игнорируем ошибки, если виджет уже уничтожен
            pass

    def destroy(self):
        """Вызывается при уничтожении виджета"""
        self.is_destroyed = True
        self.clear_image()

        # Закрываем PIL Image, если он еще существует
        if self.pil_image is not None:
            self.pil_image.close()
            self.pil_image = None

        # Очищаем ссылку на Tkinter image
        self.tk_image = None