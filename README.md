# Music Symbols Recognition System

## Описание

**Music Symbols Recognition System** — проект для автоматизации распознавания музыкальных символов на изображениях нотных листов с помощью компьютерного зрения и нейросетей.

Включает:
- инструменты для ручной разметки и подготовки датасета,
- модули для препроцессинга и нарезки изображений,
- инфраструктуру для обучения и тестирования моделей.

---

## Структура проекта

```
project-root/
├── input/                # Исходные изображения для разметки
├── output/               # Результаты ручной разметки
│   ├── positive/         # Классы размеченных символов
│   ├── negative/         # Негативные примеры
│   └── labels.txt        # Аннотации: имя файла, класс (англ.)
├── symbol_labeler/       # Инструменты для ручной сортировки и аннотирования
│   ├── labeler.py        # Графическая утилита для разметки
│   ├── symbols.txt       # Список классов для разметки (русские названия)
│   └── class_map.txt     # Соответствие: русское название → английское имя класса
├── recognize/            # Модули и данные для обучения и инференса
│   ├── positive_images/  # Папки с изображениями по классам (после разметки)
│   └── negative_images/  # Папка с негативными примерами
├── dataset/              # Готовый датасет для обучения (ImageFolder)
│   ├── train/
│   │   ├── clef_g/
│   │   ├── flat/
│   │   ├── note_head_quarter/
│   │   ├── ...
│   │   └── negative/
│   └── val/
│       ├── clef_g/
│       ├── flat/
│       ├── note_head_quarter/
│       ├── ...
│       └── negative/
└── prepare_dataset.py    # Скрипт для подготовки датасета
```

---

## Быстрый старт

### 1. Ручная разметка изображений
- Поместите неразмеченные изображения в папку `input/`.
- Запустите разметчик:
  ```bash
  python symbol_labeler/labeler.py
  ```
- Используйте горячие клавиши для сортировки по классам (см. `symbols.txt`).
- После разметки изображения перемещаются в `output/positive/<класс>/` или `output/negative/`.
- Аннотации сохраняются в `output/labels.txt`.

### 2. Подготовка датасета для обучения
- После разметки скопируйте содержимое `output/positive/` и `output/negative/` в `recognize/positive_images/` и `recognize/negative_images/` соответственно (или настройте пайплайн под свою структуру).
- Запустите скрипт подготовки датасета:
  ```bash
  python prepare_dataset.py
  ```
- В результате появится папка `dataset/` с подпапками `train/` и `val/`, где изображения будут разложены по классам и разделены в соотношении 80/20.
- Структура полностью совместима с `torchvision.datasets.ImageFolder`:
  - `dataset/train/<class_name>/*.png`
  - `dataset/val/<class_name>/*.png`

### 3. Использование датасета
- Для обучения моделей используйте папку `dataset/` с любым фреймворком, поддерживающим ImageFolder.

---

## prepare_dataset.py

Скрипт для автоматической подготовки датасета:
- Очищает и пересоздаёт папки `dataset/train/` и `dataset/val/` для каждого класса.
- Случайным образом делит изображения на train и val (80/20).
- Поддерживает структуру, совместимую с ImageFolder.

**Пример кода:**
```python
import os
import shutil
import random
from pathlib import Path

SOURCE_POS = Path("recognize/positive_images")
SOURCE_NEG = Path("recognize/negative_images")
DEST = Path("dataset")
SPLIT_RATIO = 0.8  # 80% train, 20% val

def prepare_dir(path):
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)

def split_and_copy(src_paths, train_dir, val_dir):
    random.shuffle(src_paths)
    split_idx = int(len(src_paths) * SPLIT_RATIO)
    train_files = src_paths[:split_idx]
    val_files = src_paths[split_idx:]

    for f in train_files:
        shutil.copy(f, train_dir / f.name)
    for f in val_files:
        shutil.copy(f, val_dir / f.name)

def main():
    random.seed(42)

    for split in ['train', 'val']:
        for cls in os.listdir(SOURCE_POS):
            prepare_dir(DEST / split / cls)
        prepare_dir(DEST / split / 'negative')

    for cls in os.listdir(SOURCE_POS):
        cls_path = SOURCE_POS / cls
        if not cls_path.is_dir():
            continue
        files = list(cls_path.glob("*.png"))
        split_and_copy(files, DEST / 'train' / cls, DEST / 'val' / cls)

    neg_files = list(SOURCE_NEG.glob("*.png"))
    split_and_copy(neg_files, DEST / 'train' / 'negative', DEST / 'val' / 'negative')

    print("✅ Датасет собран в папке /dataset")

if __name__ == "__main__":
    main()
```

---

## symbols.txt
- Список всех классов для разметки (по одному в строке).
- Для добавления нового класса просто добавьте его название в этот файл.

## class_map.txt
- Соответствие между русскими названиями классов (для интерфейса) и английскими идентификаторами (для структуры папок и аннотаций). Формат:
  `Русское название:английское_имя`

---

## Служебные скрипты

### clear_output.py

Скрипт `output/clear_output.py` очищает папку `output/` от всех файлов и папок, кроме служебных файлов `.gitkeep` и самого скрипта `clear_output.py`.

**Использование:**
```bash
python output/clear_output.py
```

- После запуска все размеченные изображения, аннотации и подпапки в `output/` будут удалены.
- Скрипт полезен для сброса состояния перед новой разметкой или тестированием.
- **Внимание:** восстановить удалённые данные будет невозможно!

---


