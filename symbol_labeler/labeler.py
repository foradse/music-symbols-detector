import os
import tkinter as tk
from PIL import Image, ImageTk
import shutil
import time

# Пути по умолчанию (корень проекта)
INPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'input'))
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output'))
SYMBOLS_PATH = os.path.join(os.path.dirname(__file__), 'symbols.txt')
CLASS_MAP_PATH = os.path.join(os.path.dirname(__file__), 'class_map.txt')
ANNOTATION_FILE = os.path.join(OUTPUT_DIR, 'labels.txt')

# Загрузка русских названий классов
with open(SYMBOLS_PATH, 'r', encoding='utf-8') as f:
    SYMBOL_CLASSES = [line.strip() for line in f if line.strip()]

# Загружаем соответствие русских и английских названий
CLASS_MAP = {}
with open(CLASS_MAP_PATH, 'r', encoding='utf-8') as f:
    for line in f:
        if ':' in line:
            ru, en = line.strip().split(':', 1)
            CLASS_MAP[ru.strip()] = en.strip()

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

CLASSES_PER_PAGE = 10

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
        self.history = []

        self.bg = '#232323'
        self.fg = '#cccccc'
        self.btn_bg = '#2d2d2d'
        self.btn_fg = '#e0e0e0'
        self.btn_active = '#444444'
        self.frame_bg = '#232323'

        self.num_buffer = ''
        self.last_num_time = 0
        self.num_timeout = 1.0  # секунды для ввода многозначного номера

        self.root.configure(bg=self.bg)

        # --- Слева: Listbox с классами ---
        self.left_frame = tk.Frame(root, bg=self.frame_bg)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=18, pady=18)
        self.class_listbox = tk.Listbox(self.left_frame, width=24, height=18, font=("Consolas", 15),
                                        bg=self.frame_bg, fg=self.fg, selectbackground='#444', activestyle='none')
        for cls in SYMBOL_CLASSES:
            self.class_listbox.insert(tk.END, cls)
        self.class_listbox.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.class_listbox.select_set(0)
        self.class_listbox.activate(0)
        self.class_listbox.focus_set()
        self.scrollbar = tk.Scrollbar(self.left_frame, orient="vertical", command=self.class_listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.class_listbox.config(yscrollcommand=self.scrollbar.set)

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

        self.root.bind('<Key>', self.key_handler)
        self.class_listbox.bind('<Return>', self.on_enter)
        self.class_listbox.bind('<Double-Button-1>', self.on_enter)
        self.class_listbox.bind('<Up>', self.on_arrow)
        self.class_listbox.bind('<Down>', self.on_arrow)

        self.load_image()

    def load_image(self):
        if self.index >= self.total:
            self.info.config(text="Готово! Все изображения размечены.")
            self.img_label.config(image='')
            return
        img_path = os.path.join(self.image_dir, self.image_files[self.index])
        img = Image.open(img_path)
        scale = 3
        new_w = min(img.width * scale, 600)
        new_h = min(img.height * scale, 600)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        self.tkimg = ImageTk.PhotoImage(img)
        self.img_label.config(image=self.tkimg)
        self.img_label.image = self.tkimg
        self.info.config(text=f"[{self.index+1}/{self.total}] {self.image_files[self.index]}")

    def assign_label(self, class_label_ru):
        if self.index >= len(self.image_files):
            return
        fname = self.image_files[self.index]
        class_label_en = CLASS_MAP.get(class_label_ru, class_label_ru)
        with open(self.annotation_path, 'a', encoding='utf-8') as f:
            f.write(f"{fname},{class_label_en}\n")
        target_dir = os.path.join(self.output_dir, 'positive', class_label_en)
        os.makedirs(target_dir, exist_ok=True)
        src = os.path.join(self.image_dir, fname)
        dst = os.path.join(target_dir, fname)
        shutil.move(src, dst)
        self.history.append((fname, class_label_en, dst, src))
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
            return
        if os.path.exists(dst):
            shutil.move(dst, src)
        if os.path.exists(self.annotation_path):
            with open(self.annotation_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            with open(self.annotation_path, 'w', encoding='utf-8') as f:
                f.writelines(lines[:-1])
        self.image_files.insert(self.index, fname)
        self.total += 1
        self.load_image()

    def on_enter(self, event=None):
        sel = self.class_listbox.curselection()
        if sel:
            class_label = self.class_listbox.get(sel[0])
            self.assign_label(class_label)

    def on_arrow(self, event):
        return

    def key_handler(self, event):
        if self.index >= self.total:
            return
        key = event.char
        # --- Многозначный ввод номера класса ---
        if key.isdigit():
            now = time.time()
            if self.num_buffer and now - self.last_num_time > self.num_timeout:
                self.num_buffer = ''
            self.num_buffer += key
            self.last_num_time = now
            try:
                cls_index = int(self.num_buffer)
                if 1 <= cls_index <= len(SYMBOL_CLASSES):
                    self.class_listbox.selection_clear(0, tk.END)
                    self.class_listbox.select_set(cls_index - 1)
                    self.class_listbox.activate(cls_index - 1)
                    self.class_listbox.see(cls_index - 1)
            except Exception:
                self.num_buffer = ''
            return
        # --- Подтверждение выбора ---
        if event.keysym == 'Return':
            sel = self.class_listbox.curselection()
            if sel:
                class_label = self.class_listbox.get(sel[0])
                self.assign_label(class_label)
            self.num_buffer = ''
        elif event.keysym == 'n':
            self.assign_label('Негатив')
            self.num_buffer = ''
        elif event.keysym == 'x':
            self.delete_current()
            self.num_buffer = ''
        elif event.keysym == 'z':
            self.undo()
            self.num_buffer = ''
        elif event.keysym == 'q':
            self.root.quit()
            self.num_buffer = ''
        elif event.keysym == 'Up':
            cur = self.class_listbox.curselection()
            if cur and cur[0] > 0:
                self.class_listbox.selection_clear(0, tk.END)
                self.class_listbox.select_set(cur[0] - 1)
                self.class_listbox.activate(cur[0] - 1)
                self.class_listbox.see(cur[0] - 1)
            self.num_buffer = ''
        elif event.keysym == 'Down':
            cur = self.class_listbox.curselection()
            if cur and cur[0] < self.class_listbox.size() - 1:
                self.class_listbox.selection_clear(0, tk.END)
                self.class_listbox.select_set(cur[0] + 1)
                self.class_listbox.activate(cur[0] + 1)
                self.class_listbox.see(cur[0] + 1)
            self.num_buffer = ''

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Music Symbol Labeler (RU)")
    app = LabelTool(root)
    root.mainloop() 