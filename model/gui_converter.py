import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

AUDIVERIS_PATH = r"C:\Program Files\Audiveris\Audiveris.exe"
INPUT_DIR = "input"
OUTPUT_DIR = "output"

class PDFConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF → MusicXML")
        self.geometry("500x400")
        self.configure(bg="#f9f9f9")

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Выбери PDF для конвертации", font=("Arial", 12)).pack(pady=10)

        tk.Button(self, text="Выбрать файл", command=self.choose_file).pack(pady=15)

        self.progress = ttk.Progressbar(self, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=5)

        self.log_box = tk.Text(self, height=12, width=60, bg="#fcfcfc", font=("Courier", 9))
        self.log_box.pack(pady=5)
        self.log("Готово к работе.")

    def log(self, msg):
        self.log_box.insert(tk.END, msg + "\n")
        self.log_box.see(tk.END)

    def choose_file(self):
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if path:
            self.start_conversion(path)

    def start_conversion(self, pdf_path):
        thread = threading.Thread(target=self.convert_pdf, args=(pdf_path,))
        thread.start()

    def convert_pdf(self, pdf_path):
        self.progress["value"] = 0
        self.log(f"📥 Выбран файл: {pdf_path}")

        base = os.path.splitext(os.path.basename(pdf_path))[0]
        omr_path = os.path.join(OUTPUT_DIR, f"{base}.omr")
        xml_path = os.path.join(OUTPUT_DIR, f"{base}.xml")

        try:
            self.log("[1] Распознаём PDF...")
            self.progress["value"] = 30
            subprocess.run([AUDIVERIS_PATH, "-batch", "-output", OUTPUT_DIR, pdf_path], check=True)

            if not os.path.exists(omr_path):
                raise FileNotFoundError(f"Не найден .omr файл: {omr_path}")

            self.log("[2] Экспортируем в MusicXML...")
            self.progress["value"] = 70
            subprocess.run([AUDIVERIS_PATH, "-export", "-output", OUTPUT_DIR, omr_path], check=True)

            if os.path.exists(xml_path):
                self.progress["value"] = 100
                self.log(f"✅ Готово! XML: {xml_path}")
                messagebox.showinfo("Успех", f"XML сохранён: {xml_path}")
            else:
                raise FileNotFoundError(f"XML не найден: {xml_path}")
        except Exception as e:
            self.log(f"❌ Ошибка: {e}")
            messagebox.showerror("Ошибка", str(e))

        self.progress["value"] = 0

if __name__ == "__main__":
    app = PDFConverterApp()
    app.mainloop()