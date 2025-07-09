
"""
Основной пайплайн для конвертации изображения нот в MusicXML.
Здесь используются заглушки для всех этапов, чтобы можно было тестировать структуру.
"""

import os
from pdf2image import convert_from_path
from staff_detector.split_staffs import extract_staff_regions
from symbol_detector.extract_symbols import extract_symbols
from classifier.predict import predict_symbol
from xml_exporter.export import MusicXMLExporter


def pdf_to_images(pdf_path, temp_dir="pipeline_temp_images"):
    os.makedirs(temp_dir, exist_ok=True)
    images = convert_from_path(pdf_path)
    image_paths = []
    for i, img in enumerate(images):
        img_path = os.path.join(temp_dir, f"page_{i+1}.png")
        img.save(img_path)
        image_paths.append(img_path)
    return image_paths


def process_pdf(pdf_path, output_xml="output.musicxml", model_path="models/classifier_cnn.pth", class_names=None):
    image_paths = pdf_to_images(pdf_path)
    all_symbols = []
    for page_num, image_path in enumerate(image_paths):
        staff_regions = extract_staff_regions(image_path=image_path, output_dir="pipeline_temp_staffs")
        for staff in staff_regions:
            # staff['image'] или staff, в зависимости от реализации
            symbols = extract_symbols(staff['image'] if isinstance(staff, dict) and 'image' in staff else staff)
            for symbol_img, bbox in symbols:
                result = predict_symbol(
                    image_path=symbol_img,  # если нужен путь, иначе передай массив
                    model_path=model_path,
                    class_names=class_names
                )
                all_symbols.append({
                    'image': symbol_img,
                    'bbox': bbox,
                    'class': result['class'],
                    'confidence': result['confidence']
                })
    exporter = MusicXMLExporter()
    exporter.export_from_recognition_results(all_symbols, output_xml)
    print(f"[pipeline] Готово! XML: {output_xml}")


if __name__ == "__main__":
    # Пример запуска: process_pdf("test.pdf", "result.musicxml")
    import sys
    if len(sys.argv) >= 2:
        pdf_path = sys.argv[1]
        output_xml = sys.argv[2] if len(sys.argv) > 2 else "output.musicxml"
        process_pdf(pdf_path, output_xml)
    else:
        print("Использование: python main.py <input.pdf> [output.musicxml]")