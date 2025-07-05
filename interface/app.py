from gui.main_window import MainWindow
import customtkinter as ctk


class MusicNotationApp:
    def __init__(self):
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")
        self.root = ctk.CTk()
        self.main_window = MainWindow(self.root)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = MusicNotationApp()
    app.run()