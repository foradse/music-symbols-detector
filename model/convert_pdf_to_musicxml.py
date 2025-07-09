import subprocess
import os
import sys

AUDIVERIS_PATH = r"C:\Program Files\Audiveris\Audiveris.exe"  
OUTPUT_DIR = "output"
INPUT_DIR = "input"

def convert_pdf(pdf_filename: str):
    input_path = os.path.join(INPUT_DIR, pdf_filename)
    base_name = os.path.splitext(pdf_filename)[0]
    omr_path = os.path.join(OUTPUT_DIR, f"{base_name}.omr")


    print("[1] Распознаём PDF…")
    subprocess.run([
        AUDIVERIS_PATH,
        "-batch",
        "-output", OUTPUT_DIR,
        input_path
    ], check=True)


    if not os.path.exists(omr_path):
        raise FileNotFoundError(f"Не найден файл {omr_path}")


    print("[2] Экспортируем в MusicXML…")
    subprocess.run([
        AUDIVERIS_PATH,
        "-export",
        "-output", OUTPUT_DIR,
        omr_path
    ], check=True)

    xml_path = os.path.join(OUTPUT_DIR, f"{base_name}.xml")
    if os.path.exists(xml_path):
        print(f"✅ Успешно! XML сохранён: {xml_path}")
    else:
        print(f"⚠️ Ошибка: XML не найден в {OUTPUT_DIR}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python convert_pdf_to_musicxml.py <название_файла.pdf>")
        sys.exit(1)

    filename = sys.argv[1]
    convert_pdf(filename)
