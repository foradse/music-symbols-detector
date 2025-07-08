import customtkinter as ctk


class ResultsView:
    def __init__(self, parent):
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        self.frame = ctk.CTkFrame(
            self.parent,
            fg_color="#1e1e1e",
            border_width=1,
            border_color="#444444",
            corner_radius=5,
            width=300
        )

        # Заголовок
        ctk.CTkLabel(
            self.frame,
            text="Результаты",
            font=("Arial", 14),
            text_color="white"
        ).pack(pady=5)

        self.textbox = ctk.CTkTextbox(
            self.frame,
            fg_color="#1e1e1e",
            text_color="white",
            font=("Arial", 15),
            wrap="word",
            height=200
        )
        self.textbox.pack(fill="both", expand=True, padx=10, pady=5)
        self.update_results(0, 0, 0)

    def update_results(self, staves, symbols, accuracy):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.insert("end", f"- Найдено станов: {staves}\n")
        self.textbox.insert("end", f"- Найдено символов: {symbols}\n")
        self.textbox.insert("end", f"- Точность: {accuracy}%")
        self.textbox.configure(state="disabled")

    # В классе ResultsView добавьте:
    def get_musicxml(self, image, staves=0, symbols=0, accuracy=1):
        # Тут вызываем функцию для получения MusicXML файла и данных staves, symbols, accuracy
        # передаем данные в функцию staves, symbols, accuracy в функцию ниже, а файл возвращаем
        self.update_results(staves, symbols, accuracy)
        # Временная заглушка - замените на реальную генерацию MusicXML
        return """<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
    <score-partwise version="3.0">
      <part-list>
        <score-part id="P1">
          <part-name>Music</part-name>
        </score-part>
      </part-list>
      <part id="P1">
        <measure number="1">
          <attributes>
            <divisions>1</divisions>
            <key>
              <fifths>0</fifths>
            </key>
            <time>
              <beats>4</beats>
              <beat-type>4</beat-type>
            </time>
            <clef>
              <sign>G</sign>
              <line>2</line>
            </clef>
          </attributes>
          <note>
            <pitch>
              <step>C</step>
              <octave>4</octave>
            </pitch>
            <duration>1</duration>
            <type>quarter</type>
          </note>
        </measure>
      </part>
    </score-partwise>"""

    def clear_results(self):
        """Очищает результаты анализа и сбрасывает текстовое поле"""
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.insert("end", "Результаты будут отображены здесь после обработки")
        self.textbox.configure(state="disabled")