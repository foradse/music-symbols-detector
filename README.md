# Music Symbols Detector

## Описание

**Music Symbols Detector** — система для автоматического распознавания музыкальных символов на изображениях нотных листов с помощью компьютерного зрения и нейросетей.

Система включает полный пайплайн от обработки изображений до экспорта в MusicXML формат.

---

## Структура проекта

```
project-root/
├── data_workbench/                # Инструменты и материалы для ручной разметки
│   ├── input/                     # Исходные изображения
│   ├── output/                    # Разметка
│   └── symbol_labeler/           
│       ├── labeler.py             # GUI-разметка
│       ├── symbols.txt            # Список классов
│       └── class_map.txt          # Соответствие русских и англ. названий

├── recognize/                     # Датасет с примерами по классам
│   ├── positive_images/           # Папки с примерами по классам
│   │   ├── clef_g/
│   │   ├── flat/
│   │   └── ...
│   └── negative_images/           # Папка с негативными примерами

├── dataset/                       # Основной датасет (создаётся скриптом)
│   ├── train/                     # Папки с изображениями по классам
│   └── val/

├── models/                        # Весы нейросетей
│   └── classifier_cnn.pth

├── classifier/                    # Группа 1 — Классификатор (2 человека)
│   ├── model.py                   # Архитектура нейронной сети
│   ├── train.py                   # Обучение модели
│   ├── predict.py                 # Предсказание классов
│   └── README.md                  # Документация группы

├── staff_detection/               # Группа 2 — Поиск нотных линий (2 человека)
│   ├── split_staffs.py            # Основной модуль детекции
│   └── README.md                  # Документация группы

├── symbol_detector/               # Группа 3 — Извлечение символов (2 человека)
│   ├── extract_symbols.py         # Основной модуль извлечения
│   └── README.md                  # Документация группы

├── xml_exporter/                  # Группа 4 — Экспорт в MusicXML (2 человека)
│   ├── export.py                  # Экспорт в MusicXML
│   └── README.md                  # Документация группы

├── augmentation/                  # Группа 5 — Аугментация данных (1 человек)
│   ├── augment_dataset.py         # Аугментация датасета
│   └── README.md                  # Документация группы

├── interface/                     # Группа 6 — Веб-интерфейс (1 человек)
│   ├── app.py                     # Основное приложение
│   ├── gui/                       # GUI компоненты
│   │   ├── main_window.py         # Главное окно
│   │   ├── image_viewer.py        # Просмотрщик изображений
│   │   └── results_view.py        # Отображение результатов
│   ├── utils/                     # Утилиты
│   │   ├── file_handler.py        # Обработка файлов
│   │   └── image_utils.py         # Работа с изображениями
│   └── README.md                  # Документация группы

├── pipeline/                      # Группа 7 — Интеграция пайплайна (1 человек)
│   ├── main.py                    # Основной пайплайн
│   ├── config.py                  # Конфигурация
│   ├── pipeline_manager.py        # Управление пайплайном
│   ├── data_manager.py            # Управление данными
│   ├── utils/                     # Утилиты
│   │   ├── logger.py              # Настройка логирования
│   │   ├── validators.py          # Валидация данных
│   │   └── helpers.py             # Вспомогательные функции
│   └── README.md                  # Документация группы

├── music_symbols_core.py          # Основные функции всех групп
├── build_dataset.py               # Скрипт преобразования recognize → dataset
├── requirements.txt
└── README.md
```

---

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Подготовка датасета

```bash
python build_dataset.py
```

Это создаст структуру `dataset/train/` и `dataset/val/` с папками по классам, готовую для обучения.

### 3. Обучение классификатора

```bash
cd classifier
python train.py
```

### 4. Обработка нотного листа

```bash
cd pipeline
python main.py path/to/sheet_music.png output_directory --model ../models/classifier_cnn.pth
```

### 5. Веб-интерфейс

```bash
cd interface
python app.py
```

Откройте http://localhost:5000 в браузере.

---

## Модули системы

### 1. Классификатор (`classifier/`) - Группа 1

CNN-модель для распознавания музыкальных символов.

**Файлы:**
- `model.py` - Архитектура нейронной сети
- `train.py` - Обучение модели
- `predict.py` - Предсказание классов

**Использование:**
```python
from classifier.predict import predict_symbol

result = predict_symbol(
    image_path="symbol.png",
    model_path="models/classifier_cnn.pth",
    class_names=['clef_g', 'sharp', 'flat', ...]
)
```

### 2. Детектор нотных линий (`staff_detection/`) - Группа 2

Извлечение нотных станов из изображения.

**Функции:**
- Детекция горизонтальных линий
- Группировка линий в станы
- Извлечение областей станов

### 3. Детектор символов (`symbol_detector/`) - Группа 3

Извлечение отдельных символов из нотного стана.

**Функции:**
- Удаление линий стана
- Поиск контуров символов
- Фильтрация по размеру и позиции

### 4. Экспортер XML (`xml_exporter/`) - Группа 4

Создание MusicXML файлов из результатов распознавания.

**Поддерживаемые элементы:**
- Ключи (G, F, C)
- Ноты и паузы
- Знаки альтерации
- Размеры и тональности

### 5. Аугментация (`augmentation/`) - Группа 5

Увеличение датасета с помощью трансформаций.

**Методы:**
- Поворот и масштабирование
- Добавление шума
- Изменение яркости/контрастности
- Эластичные трансформации

### 6. Веб-интерфейс (`interface/`) - Группа 6

Flask/Streamlit-приложение для загрузки и обработки изображений.

**Возможности:**
- Загрузка изображений
- Визуализация результатов
- Скачивание MusicXML

### 7. Главный пайплайн (`pipeline/`) - Группа 7

Объединение всех модулей в единый процесс.

**Этапы обработки:**
1. Извлечение нотных станов
2. Детекция символов
3. Классификация
4. Создание MusicXML
5. Генерация отчета

---

## Поддерживаемые классы символов

- **Ключи:** clef_g, clef_f, clef_c, clef_g8, clef_oct_up, clef_oct_down
- **Знаки альтерации:** sharp, flat, natural, double_sharp
- **Ноты:** note_whole, note_head_half, note_head_quarter
- **Паузы:** pause_whole_half, pause_quarter, pause_eighth, pause_sixteenth
- **Хвосты:** tail_eighth, tail_sixteenth, tail_eighth_group, tail_sixteenth_group
- **Размеры:** time_2_2, time_2_4, time_3_2, time_3_4, time_3_8, time_4_4, time_6_8, time_9_8, time_common
- **Другие:** dot, ending_1, ending_2, repeat

---

## Распределение задач по группам

| Группа | Название | Количество |
|--------|----------|------------|
| 1 | Classifier | 2 человека |
| 2 | Staff Detection | 2 человека |
| 3 | Symbol Detector | 2 человека | 
| 4 | MusicXML Export | 2 человека | 
| 5 | Augmentation | 1 человек |
| 6 | Interface | 1 человек | 
| 7 | Pipeline | 1 человек | 

---

## Основные файлы

- `music_symbols_core.py` - Содержит все основные функции и классы для всех групп
- `build_dataset.py` - Скрипт для подготовки датасета
- `requirements.txt` - Зависимости проекта


