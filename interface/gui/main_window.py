from tkinter import filedialog, messagebox
import os
from .image_viewer import ImageViewer
from .results_view import ResultsView
import customtkinter as ctk


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Symbols Detector")
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "Image", "Icon.ico")
            self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Не удалось загрузить иконку: {e}")
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        self.root.geometry(f"{width - 10}x{height - 80}+0+0")
        # Создаем основные компоненты
        self.create_widgets()
        self.setup_layout()
        self.setup_events()

    def create_widgets(self):
        # Главный контейнер
        self.main_frame = ctk.CTkFrame(self.root, fg_color="#2a2a2a")

        # Заголовок
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Music Symbols Detector",
            font=("Arial", 18, "bold"),
            text_color="white"
        )

        # Панель кнопок
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")

        # Компоненты
        self.image_viewer = ImageViewer(self.main_frame)
        self.results_view = ResultsView(self.main_frame)

        # Нижняя панель
        self.bottom_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")

        # Кнопки
        self.load_btn = ctk.CTkButton(
            self.button_frame,
            text="Загрузить изображение",
            fg_color="white",
            hover_color="#e0e0e0",
            text_color="black",
            font=("Arial", 12),
            width=180,
            height=32
        )


        # Основная область контента
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="#333333")


        self.textbox = ctk.CTkTextbox(
            self.content_frame,
            fg_color="#1e1e1e",
            text_color="white",
            font=("Arial", 15),
            wrap="word",
            height=200
        )

        self.process_btn = ctk.CTkButton(
            self.button_frame,
            text="Обработать",
            fg_color="white",
            hover_color="#e0e0e0",
            text_color="black",
            font=("Arial", 12),
            width=120,
            height=32
        )

        self.save_btn = ctk.CTkButton(
            self.bottom_frame,
            text="Сохранить MusicXML",
            fg_color="white",
            hover_color="#e0e0e0",
            text_color="black",
            font=("Arial", 12),
            width=180,
            height=32
        )

        self.clear_btn = ctk.CTkButton(
            self.bottom_frame,
            text="Очистить",
            fg_color="white",
            hover_color="#e0e0e0",
            text_color="black",
            font=("Arial", 12),
            width=120,
            height=32
        )

    def setup_layout(self):
        # Главный фрейм
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Заголовок
        self.title_label.pack(pady=(10, 10))
        self.image_viewer.frame.pack(side="left", fill="both", expand=True, padx=5, pady=(10, 10))
        # Панель кнопок
        self.button_frame.pack(fill="x", pady=10)
        self.load_btn.pack(side="left", padx=10)
        self.process_btn.pack(side="left", padx=10)

        self.content_frame.pack(fill="both", expand=True, pady=10, padx=10)
        self.textbox.pack(fill="both", expand=True, padx=10, pady=5)

        self.results_view.frame.pack(fill="both", expand=True, pady=10, padx=10)
        # Область изображения и результатов
        self.image_viewer.frame.pack(side="left", fill="both", padx=10)

        # Нижняя панель
        self.bottom_frame.pack(fill="y", pady=10, padx=10)
        self.save_btn.pack(side="left", padx=10)
        self.clear_btn.pack(side="left", padx=10)

    def setup_events(self):
        self.load_btn.configure(command=self.load_image)
        self.save_btn.configure(command=self.save_results)
        self.clear_btn.configure(command=self.clear_all)

    def load_image(self):
        # Открываем диалоговое окно для выбора файла
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Изображения", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff"), ("Все файлы", "*.*")]
        )

        # Если пользователь не выбрал файл (нажал "Отмена")
        if not file_path:
            return

        try:
            # Загружаем изображение через ImageViewer
            self.image_viewer.load_image(file_path)

            # Можно добавить дополнительную информацию о загруженном файле
            filename = os.path.basename(file_path)
            self.show_message(filename, "Изображение загружено:")


        except Exception as e:
            # Обработка ошибок
            error_msg = f"Ошибка загрузки: {str(e)}"
            print(error_msg)  # Или вывести в статус
            self.show_message(error_msg, "end")
            # Можно также показать сообщение об ошибке
            self.image_viewer.label.configure(text=error_msg, image=None)

    def save_results(self):
        # Получаем данные для сохранения (предполагаем, что results_view имеет метод get_musicxml())
        try:
            musicxml_data = self.results_view.get_musicxml()
            if not musicxml_data:
                self.show_message("Нет данных для сохранения.", "Ошибка")
                return

            # Открываем диалог сохранения файла
            file_path = filedialog.asksaveasfilename(
                defaultextension=".musicxml",
                filetypes=[("MusicXML Files", "*.musicxml"), ("XML Files", "*.xml"), ("All Files", "*.*")],
                title="Сохранить MusicXML"
            )

            if not file_path:  # Пользователь отменил сохранение
                return

            # Сохраняем данные в файл
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(musicxml_data)

            # Показываем сообщение об успешном сохранении
            self.show_message(f"Файл успешно сохранен:\n{file_path}", "Сохранение завершено.")

        except Exception as e:
            self.show_message(f"Ошибка при сохранении файла:\n{str(e)}", "Ошибка сохранения.")

    def show_message(self, message, title):
        """Вспомогательный метод для показа сообщений"""
        self.textbox.configure(state="normal")
        self.textbox.insert("end", f"{title} {message}\n")  # Или вывести в статус, если есть
        self.textbox.configure(state="disabled")

    def clear_all(self):
        """Очищает все поля и сбрасывает состояние приложения"""
        try:
            # Очищаем изображение в первую очередь
            if hasattr(self.image_viewer, 'clear_image'):
                self.image_viewer.clear_image()

            # Даем время на обновление GUI
            self.root.update_idletasks()

            # Затем очищаем остальные элементы
            self.results_view.clear_results()

            self.textbox.configure(state="normal")
            self.textbox.delete("1.0", "end")
            self.textbox.insert("end", "Готов к работе\n")
            self.textbox.configure(state="disabled")

            self.show_message("Все данные были успешно очищены", "Состояние:")

        except Exception as e:
            error_msg = f"Ошибка при очистке: {str(e)}"
            print(error_msg)
            self.show_message(error_msg, "Ошибка")