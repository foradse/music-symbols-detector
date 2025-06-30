import os
import cv2
import numpy as np
import argparse

# --- Классы символов и их фильтры (можно доработать) ---
SYMBOL_CLASSES = {
    'diez': lambda w, h: 0.55 < w/h < 1.4 and 20 < w < 700 and 20 < h < 800,  # Диез (почти квадратный, средний размер)
    'double_sharp': lambda w, h: 1.3 < w/h < 2.0 and 30 < w < 80 and 20 < h < 60,  # Двойной диез (шире обычного диеза)
    'flat': lambda w, h: h > w and 10 < w < 30 and 40 < h < 100,  # Бемоль (вертикально вытянутый)
    'natural': lambda w, h: 0.7 < w/h < 1.3 and 20 < w < 60 and 20 < h < 60,  # Натураль (почти квадратный, средний размер)
    'dot': lambda w, h: w < 20 and h < 20,  # Точка (очень маленькая, почти круглая)
    'note_head': lambda w, h: 0.7 < w/h < 1.3 and 15 < w < 40 and 15 < h < 40,  # Кружок ноты (почти круглый, средний размер)
    'pause_quarter': lambda w, h: h > w and 10 < w < 30 and 30 < h < 70,  # Пауза четвертная (вытянутая по вертикали)
    'pause_whole_half': lambda w, h: w > h and 30 < w < 70 and 10 < h < 30,  # Пауза целая/половинная (почти прямоугольник, горизонтальный)
    'clef_g': lambda w, h: h > 2*w and 20 < w < 50 and 60 < h < 150,  # Скрипичный ключ (высокий, узкий)
    'clef_f': lambda w, h: 0.7 < w/h < 1.3 and 30 < w < 70 and 30 < h < 70,  # Басовый ключ (почти круглый, крупный)
    'tail_eighth': lambda w, h: h > 2*w and 5 < w < 20 and 30 < h < 80,  # Хвостик восьмой ноты (узкий, высокий)
    'tail_sixteenth': lambda w, h: h > 2*w and 5 < w < 20 and 50 < h < 120,  # Хвостик шестнадцатой ноты (ещё выше)
    'barline': lambda w, h: w < 8 and h > 40,  # Тактовая черта (очень узкая, высокая)
    'time_signature': lambda w, h: 0.7 < w/h < 1.3 and 15 < w < 40 and 15 < h < 40,  # Цифры размера (почти квадратные, средние)
}


def prepare_output_dirs(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    # Не создаём папки для классов заранее!


def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    return thresh


def find_symbol_contours(thresh_img):
    contours, _ = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    areas = [cv2.contourArea(cnt) for cnt in contours if cv2.contourArea(cnt) > 10]

    if not areas:
        return []

    mean_area = np.mean(areas)
    std_area = np.std(areas)

    min_area = max(20, mean_area - 2 * std_area)
    max_area = mean_area + 2 * std_area

    # если 0:  расширяем на ±10%
    if min_area == max_area:
        min_area *= 0.9
        max_area *= 1.1

    print(f"[Фильтр] Мин: {int(min_area)}, Макс: {int(max_area)} (Средняя: {int(mean_area)})")

    filtered = [cnt for cnt in contours if min_area <= cv2.contourArea(cnt) <= max_area]
    return filtered


def is_probably_diez(crop):
    edges = cv2.Canny(crop, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=20, minLineLength=10, maxLineGap=3)
    if lines is None:
        return False
    vertical = 0
    horizontal = 0
    for line in lines:
        x1, y1, x2, y2 = line[0]
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        if dx < 5 and dy > 10:
            vertical += 1
        elif dy < 5 and dx > 10:
            horizontal += 1
    return vertical >= 2 and horizontal >= 2  # признак диеза


def classify_fragment(w, h, part):
    for cls, rule in SYMBOL_CLASSES.items():
        if rule(w, h):
            if cls == 'flat' and is_probably_diez(part):
                return 'diez'
            return cls
    return 'unknown'


def save_parts_and_annotations(image, contours, base_name, output_dir, prefix, ann_file):
    count = 0
    annotated_image = image.copy()

    for i, cnt in enumerate(contours):
        x, y, w, h = cv2.boundingRect(cnt)
        part = image[y:y+h, x:x+w]
        cls = classify_fragment(w, h, part)

        if cls == 'unknown':
            subfolder = 'unknown'
            class_folder = 'unknown'
        else:
            subfolder = 'positive'
            class_folder = cls
        part_dir = os.path.join(output_dir, subfolder, class_folder)
        os.makedirs(part_dir, exist_ok=True)
        print(f"Сохраняю в: {part_dir}")  # Для отладки

        part_name = f"{prefix}{base_name}_part_{i+1}.png"
        out_path = os.path.join(part_dir, part_name)
        cv2.imwrite(out_path, part)


        color = (0, 255, 0) if cls != 'unknown' else (0, 0, 255)
        cv2.rectangle(annotated_image, (x, y), (x+w, y+h), color, 2)
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        text_color = color
        text = cls
        text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        text_x = x
        text_y = y - 5 if y - 5 > text_size[1] else y + text_size[1] + 5
        cv2.putText(annotated_image, text, (text_x, text_y), font, font_scale, text_color, thickness, cv2.LINE_AA)

        ann_file.write(f"{cls}/{part_name} {x} {y} {w} {h}\n")
        count += 1

    debug_dir = os.path.join(output_dir, "debug")
    os.makedirs(debug_dir, exist_ok=True)
    annotated_path = os.path.join(debug_dir, f"{base_name}_annotated.png")
    cv2.imwrite(annotated_path, annotated_image)

    return count


def process_image(image_path, output_dir, prefix, ann_file):
    image = cv2.imread(image_path)
    thresh = preprocess_image(image)
    contours = find_symbol_contours(thresh)
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    count = save_parts_and_annotations(image, contours, base_name, output_dir, prefix, ann_file)
    print(f"{base_name}: найдено и сохранено {count} фрагментов.")


def main():
    parser = argparse.ArgumentParser(description='Автоматическая нарезка нотных символов')
    parser.add_argument('--input', type=str, default='input', help='Папка с исходными изображениями')
    parser.add_argument('--output', type=str, default='output/parts', help='Папка для сохранения фрагментов')
    parser.add_argument('--prefix', type=str, default='', help='Префикс для имён файлов')
    args = parser.parse_args()

    prepare_output_dirs(args.output)
    images = [os.path.join(args.input, f) for f in os.listdir(args.input) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
    if not images:
        print("В папке input нет изображений.")
        return
    ann_path = os.path.join(args.output, 'annotations.txt')
    with open(ann_path, 'w', encoding='utf-8') as ann_file:
        for img_path in images:
            process_image(img_path, args.output, args.prefix, ann_file)
    print(f"Готово! Аннотации сохранены в {ann_path}")

if __name__ == "__main__":
    main() 