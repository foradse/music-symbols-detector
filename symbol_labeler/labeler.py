import os
import tkinter as tk
from PIL import Image, ImageTk
import shutil

# Пути по умолчанию (корень проекта)
INPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'input'))
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output'))
SYMBOLS_PATH = os.path.join(os.path.dirname(__file__), 'symbols.txt')
ANNOTATION_FILE = os.path.join(OUTPUT_DIR, 'labels.txt')

# Загрузка классов из symbols.txt
if os.path.exists(SYMBOLS_PATH):
    with open(SYMBOLS_PATH, 'r', encoding='utf-8') as f:
        SYMBOL_CLASSES = [line.strip() for line in f if line.strip()]
else:
    SYMBOL_CLASSES = []

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

class LabelTool:
    def __init__(self, root):
        self.root = root
        self.image_dir = INPUT_DIR
        self.output_dir = OUTPUT_DIR
        self.annotation_path = ANNOTATION_FILE
        self.image_files = sorted([
            f for f in os.listdir(self.image_dir)
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ])
        self.index = 0
        self.total = len(self.image_files)

        # --- Минималистичный серый стиль ---
        self.bg = '#232323'  # фон
        self.fg = '#cccccc'  # основной текст
        self.list_fg = '#bbbbbb'  # список классов
        self.btn_bg = '#2d2d2d'  # кнопки
        self.btn_fg = '#e0e0e0'
        self.btn_active = '#444444'
        self.frame_bg = '#232323'

        self.root.configure(bg=self.bg)

        # --- Слева: вертикальный список классов ---
        self.left_frame = tk.Frame(root, bg=self.frame_bg)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=18, pady=18)

        class_list = '\n'.join([f"{i+1}. {cls}" for i, cls in enumerate(SYMBOL_CLASSES)] + ["0/n. негатив"])
        self.class_label = tk.Label(self.left_frame, text=class_list, justify=tk.LEFT, anchor='nw',
                                    fg=self.list_fg, bg=self.frame_bg, font=("Consolas", 15))
        self.class_label.pack(anchor='nw', pady=10)

        # --- Справа: изображение и инфо ---
        self.right_frame = tk.Frame(root, bg=self.bg)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=18, pady=18)

        self.img_label = tk.Label(self.right_frame, bg=self.bg)
        self.img_label.pack(pady=20)

        self.info = tk.Label(self.right_frame, text="", fg=self.fg, bg=self.bg, font=("Consolas", 13))
        self.info.pack(pady=5)

        # --- Снизу: кнопки ---
        self.bottom_frame = tk.Frame(self.right_frame, bg=self.bg)
        self.bottom_frame.pack(side=tk.BOTTOM, pady=10)
        self.btn_undo = tk.Button(self.bottom_frame, text="Отменить", width=12, height=1,
                                  bg=self.btn_bg, fg=self.btn_fg, relief=tk.FLAT,
                                  activebackground=self.btn_active, activeforeground=self.btn_fg,
                                  font=("Consolas", 12), command=self.undo)
        self.btn_undo.pack(side=tk.LEFT, padx=8)
        self.btn_delete = tk.Button(self.bottom_frame, text="Удалить", width=12, height=1,
                                    bg=self.btn_bg, fg=self.btn_fg, relief=tk.FLAT,
                                    activebackground=self.btn_active, activeforeground=self.btn_fg,
                                    font=("Consolas", 12), command=self.delete_current)
        self.btn_delete.pack(side=tk.LEFT, padx=8)
        self.btn_quit = tk.Button(self.bottom_frame, text="Закрыть", width=12, height=1,
                                  bg=self.btn_bg, fg=self.btn_fg, relief=tk.FLAT,
                                  activebackground=self.btn_active, activeforeground=self.btn_fg,
                                  font=("Consolas", 12), command=self.root.quit)
        self.btn_quit.pack(side=tk.LEFT, padx=8)

        # --- Горячие клавиши ---
        self.root.bind("<Key>", self.key_handler)

        self.history = []  # для отмены
        self.load_image()

    def load_image(self):
        if self.index >= self.total:
            self.info.config(text="Готово! Все изображения размечены.")
            self.img_label.config(image='')
            return
        img_path = os.path.join(self.image_dir, self.image_files[self.index])
        img = Image.open(img_path)
        # Увеличиваем изображение ×3 (но не более 600x600)
        scale = 3
        new_w = min(img.width * scale, 600)
        new_h = min(img.height * scale, 600)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        self.tkimg = ImageTk.PhotoImage(img)
        self.img_label.config(image=self.tkimg)
        self.img_label.image = self.tkimg
        self.info.config(text=f"[{self.index+1}/{self.total}] {self.image_files[self.index]}")

    def assign_label(self, class_label):
        if self.index >= len(self.image_files):
            return
        fname = self.image_files[self.index]
        # Сохраняем аннотацию
        with open(self.annotation_path, 'a', encoding='utf-8') as f:
            f.write(f"{fname},{class_label}\n")
        # Перемещаем файл в output/positive/class_label или output/negative
        if class_label == 'negative':
            target_dir = os.path.join(self.output_dir, 'negative')
        else:
            target_dir = os.path.join(self.output_dir, 'positive', class_label)
        os.makedirs(target_dir, exist_ok=True)
        src = os.path.join(self.image_dir, fname)
        dst = os.path.join(target_dir, fname)
        shutil.move(src, dst)
        self.history.append((fname, class_label, dst, src))  # для undo
        del self.image_files[self.index]
        self.total -= 1
        self.load_image()

    def delete_current(self):
        if self.index >= len(self.image_files):
            return
        fname = self.image_files[self.index]
        os.remove(os.path.join(self.image_dir, fname))
        self.history.append((fname, 'deleted', None, os.path.join(self.image_dir, fname)))
        del self.image_files[self.index]
        self.total -= 1
        self.load_image()

    def undo(self):
        if not self.history:
            return
        last = self.history.pop()
        fname, label, dst, src = last
        if label == 'deleted':
            # восстановить удалённый файл невозможно (можно только отменить последнее перемещение)
            return
        # Переместить обратно
        if os.path.exists(dst):
            shutil.move(dst, src)
        # Удалить последнюю строку из аннотации
        if os.path.exists(self.annotation_path):
            with open(self.annotation_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            with open(self.annotation_path, 'w', encoding='utf-8') as f:
                f.writelines(lines[:-1])
        # Вернуть в список
        self.image_files.insert(self.index, fname)
        self.total += 1
        self.load_image()

    def key_handler(self, event):
        if self.index >= self.total:
            return
        key = event.char
        if key.isdigit():
            cls_index = int(key)
            if cls_index == 0:
                self.assign_label('negative')
            elif 1 <= cls_index <= len(SYMBOL_CLASSES):
                self.assign_label(SYMBOL_CLASSES[cls_index - 1])
        elif key == 'n':
            self.assign_label('negative')
        elif key == 'x':
            self.delete_current()
        elif key == 'z':
            self.undo()
        elif key == 'q':
            self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Symbol Labeler (Minimalist)")
    app = LabelTool(root)
    root.mainloop() 