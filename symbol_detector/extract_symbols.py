import cv2 as cv
import numpy as np
import os
import sys
import json

def estimate_line_thickness(binary_img):
    vertical_proj = np.sum(binary_img, axis=1)
    norm_proj = vertical_proj / np.max(vertical_proj) if np.max(vertical_proj) > 0 else vertical_proj
    line_indices = np.where(norm_proj > 0.5)[0]
    if len(line_indices) == 0:
        return 2
    groups = np.split(line_indices, np.where(np.diff(line_indices) != 1)[0]+1)
    thicknesses = [len(g) for g in groups if len(g) > 0]
    thickness = int(np.median(thicknesses)) if thicknesses else 2
    return max(1, min(thickness, 4))

def remove_staff_lines(staff_image):
    input_path = staff_image.replace('\\', '/')
    im = cv.imread(input_path)
    assert im is not None, f"Файл {input_path} не удалось прочитать"
    gray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)

    _, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)
    h, w = binary.shape

    line_thickness = estimate_line_thickness(binary)

    horiz_length = max(20, min(w // 10, 60))
    vert_length = h - 3

    horizontal_kernel = cv.getStructuringElement(cv.MORPH_RECT, (horiz_length, line_thickness))
    vertical_kernel = cv.getStructuringElement(cv.MORPH_RECT, (line_thickness, vert_length))

    horizontal_lines = cv.morphologyEx(binary, cv.MORPH_OPEN, horizontal_kernel, iterations=1)
    vertical_lines = cv.morphologyEx(binary, cv.MORPH_OPEN, vertical_kernel, iterations=1)
    line_mask = cv.bitwise_or(horizontal_lines, vertical_lines)

    num_labels, labels, stats, _ = cv.connectedComponentsWithStats(line_mask, connectivity=8)
    filtered_mask = np.zeros_like(line_mask)
    min_line_length = max(20, horiz_length // 4)
    for i in range(1, num_labels):
        x, y, w_box, h_box, area = stats[i]
        if w_box > min_line_length or h_box > min_line_length:
            filtered_mask[labels == i] = 255

    inpainted = cv.inpaint(gray, filtered_mask, inpaintRadius=7, flags=cv.INPAINT_TELEA)
    _, binary2 = cv.threshold(inpainted, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)

    vert_close_kernel = cv.getStructuringElement(cv.MORPH_RECT, (1, max(2, line_thickness)))
    cleaned = cv.morphologyEx(binary2, cv.MORPH_CLOSE, vert_close_kernel, iterations=1)
    horiz_close_kernel = cv.getStructuringElement(cv.MORPH_RECT, (max(2, line_thickness), max(3, line_thickness)))
    cleaned = cv.morphologyEx(cleaned, cv.MORPH_CLOSE, horiz_close_kernel, iterations=1)
    noise_kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (1, max(3, line_thickness * 2)))
    cleaned = cv.morphologyEx(cleaned, cv.MORPH_OPEN, noise_kernel)
    kernel = np.ones((2, 2), np.uint8)
    cleaned = cv.erode(cleaned, kernel, iterations=1)

    result = cv.bitwise_not(cleaned)
    output_path = os.path.join(os.path.dirname(input_path), "cleaned_auto.jpg")
    cv.imwrite(output_path, result)
    print(f"Результат сохранён: {output_path} (толщина линий: {line_thickness})")
    return output_path

def find_symbol_contours(cleaned_image, min_area=50, max_area=5000):
    contours, _ = cv.findContours(cleaned_image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    symbol_boxes = []
    for cnt in contours:
        x, y, w, h = cv.boundingRect(cnt)
        area = w * h
        if min_area <= area <= max_area:
            symbol_boxes.append((x, y, w, h))
    return symbol_boxes

def extract_symbols(image_path, output_dir="extracted_symbols"):
    cleaned_path = remove_staff_lines(image_path)

    cleaned_image = cv.imread(cleaned_path, cv.IMREAD_GRAYSCALE)
    if cleaned_image is None:
        raise ValueError("Не удалось загрузить очищенное изображение.")

    # Инвертируем для поиска контуров
    _, binary_for_contours = cv.threshold(cleaned_image, 127, 255, cv.THRESH_BINARY_INV)

    symbol_boxes = find_symbol_contours(binary_for_contours)
    os.makedirs(output_dir, exist_ok=True)

    output = []
    for idx, (x, y, w, h) in enumerate(symbol_boxes):
        symbol_img = cleaned_image[y:y+h, x:x+w]
        resized = cv.resize(symbol_img, (64, 64))
        filename = f"symbol_{idx}.png"
        path = os.path.join(output_dir, filename)
        cv.imwrite(path, resized)
        output.append({"filename": filename, "bbox": [x, y, w, h]})


    json_path = os.path.join(output_dir, "symbol_coords.json")
    with open(json_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Извлечено {len(output)} символов. Координаты сохранены в {json_path}")
    return output

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Использование:")
        print("  python extract_symbols.py remove_staff_lines <путь_к_изображению>")
        print("  python extract_symbols.py extract_symbols <путь_к_изображению>")
        sys.exit(1)

    command = sys.argv[1]
    image_path = sys.argv[2]

    if command == "remove_staff_lines":
        remove_staff_lines(image_path)
    elif command == "extract_symbols":
        extract_symbols(image_path)
    else:
        print("Неизвестная команда.")
        sys.exit(1)
