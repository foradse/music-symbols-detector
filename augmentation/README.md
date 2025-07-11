# Группа 5: Автоматическое расширение датасета (Augmentation)

## Задача
Брать уже готовые картинки и автоматически искажать их: поворачивать, добавлять шум, менять яркость. Так модель будет обучаться лучше.

## Команда
1 человек

## Что нужно сделать

### 1. Базовые трансформации
- **Поворот:** случайный поворот на ±15 градусов
- **Масштабирование:** изменение размера на ±10%
- **Сдвиг:** перемещение на ±5 пикселей
- **Отражение:** горизонтальное отражение (опционально)

### 2. Изменение яркости и контрастности
- **Яркость:** изменение на ±20%
- **Контрастность:** изменение на ±20%
- **Гамма-коррекция:** изменение на ±0.2

### 3. Добавление шума и артефактов
- **Гауссов шум:** добавление случайного шума
- **Соль и перец:** случайные белые и черные точки
- **Размытие:** легкое размытие изображения
- **Резкость:** увеличение резкости

### 4. Эластичные трансформации
- **Эластичная деформация:** имитация искажений бумаги
- **Перспективные искажения:** имитация наклона камеры
- **Морфологические операции:** эрозия и дилатация

### 5. Пакетная обработка
- Обработка всего датасета
- Сохранение оригиналов + аугментированных версий
- Создание структуры папок
- Логирование процесса

## Технологии
- **OpenCV** - основная библиотека для обработки изображений
- **PIL (Pillow)** - для изменения яркости и контрастности
- **numpy** - для математических операций
- **torchvision** - для некоторых трансформаций
- **random** - для генерации случайных параметров

## Структура файлов
```
augmenter/
├── augment_dataset.py  # Основной модуль аугментации
└── README.md           # Этот файл
```

## Как запустить

### Основная функция:
```python
from augment_dataset import MusicSymbolAugmenter

# Создание аугментатора
augmenter = MusicSymbolAugmenter()

# Аугментация одного изображения
augmented_paths = augmenter.augment_single_image(
    image_path="path/to/symbol.png",
    output_dir="augmented_symbols",
    augmentations_per_image=5
)
```

### Аугментация всего датасета:
```python
from augment_dataset import create_augmentation_pipeline

# Создание аугментированного датасета
create_augmentation_pipeline()
```

### Ручная аугментация:
```python
from augment_dataset import MusicSymbolAugmenter

augmenter = MusicSymbolAugmenter()

# Поворот
rotated = augmenter.rotate_image(image, angle=10)

# Добавление шума
noisy = augmenter.add_noise(image, noise_factor=0.1)

# Изменение яркости
brighter = augmenter.adjust_brightness(image, factor=1.2)
```

## Входные данные
- Изображения из `dataset/train/` и `dataset/val/`
- Формат: PNG, JPG
- Размер: 64x64 пикселей (grayscale)

## Выходные данные
- Аугментированные изображения в `dataset/train_augmented/` и `dataset/val_augmented/`
- Сохранение оригиналов + новые версии
- Структура папок по классам

## Цели
1. **Качество аугментации:** реалистичные искажения
2. **Разнообразие:** много вариантов каждого изображения
3. **Производительность:** быстрая обработка больших датасетов
4. **Совместимость:** работа с существующей структурой

## Критерии готовности
- [ ] Функция `augment_single_image()` работает корректно
- [ ] Функция `augment_dataset()` обрабатывает весь датасет
- [ ] Создано > 3 аугментации на изображение
- [ ] Аугментированные изображения выглядят реалистично
- [ ] Сохранена структура папок по классам
- [ ] Код обрабатывает ошибки (поврежденные файлы, нехватка места)
- [ ] Документация функций написана

## Связь с другими группами
- **Вход:** датасет из `dataset/` (создается `build_dataset.py`)
- **Выход:** аугментированный датасет для группы 1 (classifier)
- **Тестирование:** используйте изображения из `recognize_old/`

## Алгоритм работы
1. **Загрузка изображения:**
   - Чтение файла
   - Проверка формата
   - Конвертация в grayscale

2. **Применение трансформаций:**
   - Случайный выбор типа трансформации
   - Применение с случайными параметрами
   - Проверка качества результата

3. **Сохранение:**
   - Генерация имени файла
   - Сохранение в нужную папку
   - Обновление счетчиков

4. **Пакетная обработка:**
   - Обход всех папок и файлов
   - Параллельная обработка
   - Логирование прогресса

## Тестирование
1. **Простые случаи:** базовые трансформации
2. **Сложные случаи:** комбинации трансформаций
3. **Граничные случаи:** очень маленькие/большие изображения

## Советы
1. Начните с простых трансформаций
2. Тестируйте на небольшом датасете
3. Следите за качеством аугментированных изображений
4. Добавьте прогресс-бар для больших датасетов
5. Сохраняйте промежуточные результаты

## Если застряли
1. Проверьте формат входных изображений
2. Уменьшите количество аугментаций для отладки
3. Посмотрите примеры в OpenCV документации
4. Проверьте свободное место на диске
5. Обратитесь к Адлану за помощью

## Полезные ссылки
- [OpenCV Image Processing](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)
- [PIL ImageEnhance](https://pillow.readthedocs.io/en/stable/reference/ImageEnhance.html)
- [torchvision Transforms](https://pytorch.org/vision/stable/transforms.html)

## Параметры аугментации

### Рекомендуемые настройки:
```python
# Поворот
rotation_range = (-15, 15)  # градусы

# Масштабирование
scale_range = (0.9, 1.1)    # множитель

# Сдвиг
translation_range = (-5, 5)  # пиксели

# Яркость и контрастность
brightness_range = (0.8, 1.2)
contrast_range = (0.8, 1.2)

# Шум
noise_factor_range = (0.05, 0.15)

# Количество аугментаций
augmentations_per_image = 3  # для train
augmentations_per_image = 1  # для val
```

## Ожидаемые результаты
- **Увеличение датасета:** в 3-5 раз
- **Улучшение точности модели:** +5-10%
- **Устойчивость к искажениям:** +15-20%
- **Время обработки:** < 10 минут на весь датасет 