import cv2
import numpy as np
import os
from typing import List, Tuple, Dict


class StaffDetector:
    def __init__(self, image_path: str):
        """
        Инициализация детектора нотных станов

        Args:
            image_path: путь к изображению нотного листа
        """

        self.contrasted = None
        self.blur = None
        self.image_path = image_path
        self.image = None
        self.gray = None
        self.binary = None
        self.horizontal_lines = []
        self.staffs = []
        self.staff_regions = []
        self.load_image()

    def load_image(self):
        """Загрузка и предобработка изображения"""
        self.image = cv2.imread(self.image_path)
        if self.image is None:
            raise ValueError(f"Не удалось загрузить изображение: {self.image_path}")

        self.contrasted = cv2.convertScaleAbs(self.image, alpha=1, beta=0)

        self.blur = cv2.GaussianBlur(self.contrasted, (1, 1), 0)

        # Преобразование в градации серого
        self.gray = cv2.cvtColor(self.blur, cv2.COLOR_BGR2GRAY)

        # Бинаризация изображения
        self.binary = cv2.threshold(
            self.gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )[1]

    def detect_horizontal_lines(self,
                                min_line_length: int = 250,
                                max_line_gap: int = 10):
        """
        Обнаружение горизонтальных линий на изображении

        Args:
            min_line_length: минимальная длина линии для детекции
            max_line_gap: максимальный разрыв в линии
        """
        # Морфологическое открытие для выделения горизонтальных линий
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))
        opened = cv2.morphologyEx(self.binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

        # Нахождение контуров
        contours = cv2.findContours(opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]

        # Фильтрация и преобразование контуров в линии
        self.horizontal_lines = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > min_line_length:  # Фильтр по длине линии
                self.horizontal_lines.append((x, y, x + w - 1, y))

    def group_lines_into_staffs(self,
                                max_line_gap: int = 30,
                                min_lines_in_staff: int = 4):
        """
        Группировка линий в нотные станы

        Args:
            max_line_gap: максимальное расстояние между линиями в одном стане
            min_lines_in_staff: минимальное количество линий для образования стана
        """
        # Сортируем линии по Y-координате
        sorted_lines = sorted(self.horizontal_lines, key=lambda x: x[1])

        self.staffs = []
        current_staff = []

        for i, line in enumerate(sorted_lines):
            if not current_staff:
                current_staff.append(line)
            else:
                last_line = current_staff[-1]
                # Проверяем расстояние до предыдущей линии
                if abs(line[1] - last_line[1]) <= max_line_gap:
                    current_staff.append(line)
                else:
                    # Если группа закончилась, сохраняем стан
                    if len(current_staff) >= min_lines_in_staff:
                        self.staffs.append(self._create_staff(current_staff))
                    current_staff = [line]

        # Добавляем последнюю группу
        if len(current_staff) >= min_lines_in_staff:
            self.staffs.append(self._create_staff(current_staff))

    def _create_staff(self, lines: List[Tuple[int, int, int, int]]) -> Dict:
        """
        Создает описание стана из группы линий

        Args:
            lines: список линий стана

        Returns:
            Словарь с информацией о стане
        """
        # Сортируем линии по Y-координате
        sorted_lines = sorted(lines, key=lambda x: x[1])

        # Определяем границы стана
        top = sorted_lines[0][1]
        bottom = sorted_lines[-1][1]
        left = 0
        right = self.image.shape[1] - 1

        # Вычисляем среднее расстояние между линиями
        distances = []
        for i in range(1, len(sorted_lines)):
            distances.append(sorted_lines[i][1] - sorted_lines[i - 1][1])
        avg_distance = sum(distances) / len(distances) if distances else 0

        return {
            'lines': sorted_lines,
            'top': top,
            'bottom': bottom,
            'left': left,
            'right': right,
            'line_count': len(sorted_lines),
            'avg_line_distance': avg_distance,
            'height': bottom - top
        }

    def extract_staff_areas(self, output_dir: str = None) -> List[Dict]:
        """
        Извлечение областей станов из изображения

        Args:
            output_dir: директория для сохранения (опционально)

        Returns:
            Список словарей с информацией о вырезанных станах
        """
        self.staff_regions = []

        for i, staff in enumerate(self.staffs):
            # Добавляем отступы сверху и снизу
            padding = int(staff['avg_line_distance'] * 1.5)
            y1 = max(0, staff['top'] - padding)
            y2 = min(self.image.shape[0] - 1, staff['bottom'] + padding)

            # Вырезаем область стана
            staff_region = self.image[y1:y2, staff['left']:staff['right']]

            # Сохраняем информацию о стане
            staff_info = {
                'id': i,
                'image': staff_region,
                'coordinates': {
                    'left': staff['left'],
                    'top': y1,
                    'right': staff['right'],
                    'bottom': y2,
                    'width': staff['right'] - staff['left'],
                    'height': y2 - y1
                },
                'line_count': staff['line_count'],
                'original_size': self.image.shape[:2]
            }

            # Сохраняем в файл если указана директория
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f'staff_{i}.png')
                cv2.imwrite(output_path, staff_region)
                staff_info['output_path'] = output_path

            self.staff_regions.append(staff_info)

        return self.staff_regions

    def visualize(self,
                  output_path: str = None,
                  line_color: Tuple[int, int, int] = (0, 0, 255),
                  staff_color: Tuple[int, int, int] = (0, 255, 0)) -> np.ndarray:
        """
        Визуализация результатов обнаружения станов

        Args:
            output_path: путь для сохранения результата (опционально)
            line_color: цвет для отображения линий (BGR)
            staff_color: цвет для отображения границ станов (BGR)

        Returns:
            Изображение с визуализацией
        """
        # Создаем копию изображения для рисования
        vis_img = self.image.copy()

        # Рисуем линии
        for line in self.horizontal_lines:
            cv2.line(vis_img, (line[0], line[1]), (line[2], line[3]), line_color, 2)

        # Рисуем станы
        for i, staff in enumerate(self.staffs):
            # Рисуем прямоугольник вокруг стана
            cv2.rectangle(
                vis_img,
                (staff['left'], staff['top']),
                (staff['right'], staff['bottom']),
                staff_color, 2
            )

            # Подписываем номер стана
            cv2.putText(
                vis_img, f"Staff {i}",
                (staff['left'] + 10, staff['top'] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, staff_color, 1
            )

        # Сохраняем если указан путь
        if output_path:
            cv2.imwrite(output_path, vis_img)

        return vis_img

    def print_coordinates(self):
        """Вывод координат обнаруженных станов"""
        if not self.staff_regions:
            print("Станы не обнаружены. Сначала выполните extract_staff_areas().")
            return

        print(f"Найдено {len(self.staff_regions)} нотных станов:")
        for i, region in enumerate(self.staff_regions):
            coords = region['coordinates']
            print(f"Стан {i}:")
            print(f"  Координаты: (L:{coords['left']}, T:{coords['top']}, "
                  f"R:{coords['right']}, B:{coords['bottom']})")
            print(f"  Размер: {coords['width']}x{coords['height']} пикселей")
            print(f"  Количество линий: {region['line_count']}")

    def run_pipeline(self, output_dir: str = None):
        """
        Запуск полного пайплайна обработки

        Args:
            output_dir: директория для сохранения результатов (опционально)
        """
        self.detect_horizontal_lines()
        self.group_lines_into_staffs()
        self.extract_staff_areas(output_dir)
        self.print_coordinates()

        return self.staff_regions


if __name__ == '__main__':
    # Пример использования класса
    detector = StaffDetector("test.png")

    # Запуск полного пайплайна обработки
    staff_regions = detector.run_pipeline(output_dir="extracted_staffs")

    # Дополнительное сохранение визуализации
    detector.visualize(output_path="detection_result.png")

    print("Обработка завершена!")