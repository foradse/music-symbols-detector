# Группа 7: Интеграция всех частей в одну программу (Pipeline)

## Задача
Собрать все части в один рабочий скрипт. Загружаем файл — получаем готовый музыкальный XML.

## Команда
1 человек

## Что нужно сделать

### 1. Создание основного пайплайна
- **Оркестрация модулей:** координация работы всех групп
- **Последовательность обработки:** правильный порядок вызовов
- **Обработка ошибок:** graceful handling ошибок на каждом этапе
- **Логирование:** подробные логи процесса

### 2. Интеграция всех модулей
- **Группа 2 (staff_detector):** детекция нотных строк
- **Группа 3 (symbol_detector):** извлечение символов
- **Группа 1 (classifier):** классификация символов
- **Группа 4 (xml_exporter):** создание MusicXML
- **Группа 5 (augmenter):** аугментация (опционально)

### 3. Управление данными
- **Временные файлы:** создание и очистка
- **Передача данных:** между этапами пайплайна
- **Кэширование:** для ускорения повторных запусков
- **Валидация:** проверка промежуточных результатов

### 4. Оптимизация производительности
- **Параллельная обработка:** где возможно
- **Память:** эффективное использование
- **Время выполнения:** мониторинг и оптимизация
- **Масштабируемость:** работа с большими файлами

## Технологии
- **Python** - основной язык
- **multiprocessing** - для параллельной обработки
- **logging** - для логирования
- **json** - для конфигурации
- **pathlib** - для работы с путями

## Структура файлов
```
pipeline/
├── main.py              # Основной пайплайн
├── config.py            # Конфигурация
├── pipeline_manager.py  # Управление пайплайном
├── data_manager.py      # Управление данными
├── utils/               # Утилиты
│   ├── logger.py        # Настройка логирования
│   ├── validators.py    # Валидация данных
│   └── helpers.py       # Вспомогательные функции
└── README.md            # Этот файл
```

## Как запустить

### Основной пайплайн:
```bash
cd pipeline
python main.py --input "path/to/sheet_music.png" --output "result.musicxml"
```

### Программный запуск:
```python
from pipeline.main import MusicSymbolPipeline

# Создание пайплайна
pipeline = MusicSymbolPipeline()

# Обработка изображения
result = pipeline.process_image(
    input_path="path/to/sheet_music.png",
    output_path="result.musicxml",
    config_path="config.json"
)

print(f"Обработано станов: {result['staffs_count']}")
print(f"Найдено символов: {result['symbols_count']}")
print(f"Точность: {result['accuracy']:.2f}%")
```

### Конфигурация:
```python
from pipeline.config import PipelineConfig

# Загрузка конфигурации
config = PipelineConfig.from_file("config.json")

# Изменение параметров
config.staff_detection.min_line_length = 100
config.classifier.confidence_threshold = 0.8
config.xml_export.title = "My Music"

# Сохранение
config.save("new_config.json")
```

## Входные данные
- Изображения нотных листов (PNG, JPG, TIFF, BMP)
- Конфигурационный файл (опционально)
- Путь для сохранения результатов

## Выходные данные
- MusicXML файл
- Отчет о обработке (JSON)
- Логи процесса
- Временные файлы (опционально)

## Цели
1. **Надежность:** стабильная работа без крашей
2. **Производительность:** быстрая обработка
3. **Модульность:** легко добавлять новые компоненты
4. **Мониторинг:** подробная информация о процессе

## Критерии готовности
- [ ] Функция `process_image()` работает корректно
- [ ] Все модули интегрированы и работают вместе
- [ ] Обрабатываются ошибки на каждом этапе
- [ ] Создается валидный MusicXML файл
- [ ] Ведется подробное логирование
- [ ] Конфигурация загружается из файла
- [ ] Временные файлы очищаются
- [ ] Документация функций написана

## Связь с другими группами
- **Координация:** всех групп (1-6)
- **Вход:** изображения от группы 6 (interface)
- **Выход:** MusicXML для группы 6 (interface)
- **Конфигурация:** настройки для всех модулей

## Алгоритм работы пайплайна

### 1. Инициализация:
```python
# Загрузка конфигурации
config = PipelineConfig.from_file(config_path)

# Инициализация логгера
logger = setup_logger(config.logging)

# Проверка входных данных
validate_input_image(input_path)
```

### 2. Детекция станов (Группа 2):
```python
# Извлечение нотных строк
staff_regions = staff_detector.extract_staff_regions(
    image_path=input_path,
    config=config.staff_detection
)

logger.info(f"Найдено {len(staff_regions)} нотных станов")
```

### 3. Извлечение символов (Группа 3):
```python
all_symbols = []
for i, staff in enumerate(staff_regions):
    symbols = symbol_detector.extract_symbols_from_staff(
        staff_image=staff.image,
        config=config.symbol_detection
    )
    all_symbols.extend(symbols)
    logger.info(f"Стан {i+1}: найдено {len(symbols)} символов")
```

### 4. Классификация символов (Группа 1):
```python
classified_symbols = []
for symbol in all_symbols:
    result = classifier.predict_symbol(
        symbol_image=symbol.image,
        model_path=config.classifier.model_path,
        confidence_threshold=config.classifier.confidence_threshold
    )
    if result['confidence'] > config.classifier.confidence_threshold:
        classified_symbols.append({
            'symbol': symbol,
            'class': result['class'],
            'confidence': result['confidence']
        })
```

### 5. Экспорт в MusicXML (Группа 4):
```python
xml_exporter = MusicXMLExporter(config.xml_export)
xml_exporter.export_from_recognition_results(
    results=classified_symbols,
    output_file=output_path
)
```

### 6. Очистка:
```python
# Удаление временных файлов
cleanup_temp_files(config.temp_dir)

# Создание отчета
create_report(result_data, output_path)
```

## Тестирование
1. **Простые случаи:** одно изображение, один стан
2. **Сложные случаи:** много станов, много символов
3. **Граничные случаи:** пустые изображения, ошибки модулей

## Советы
1. Начните с простого пайплайна
2. Добавляйте логирование с самого начала
3. Тестируйте каждый этап отдельно
4. Используйте конфигурационные файлы
5. Обрабатывайте ошибки gracefully

## Если застряли
1. Проверьте логи для диагностики
2. Тестируйте модули по отдельности
3. Убедитесь, что все зависимости установлены
4. Проверьте пути к файлам
5. Обратитесь к Адлану за помощью

## Полезные ссылки
- [Python Logging](https://docs.python.org/3/library/logging.html)
- [Python Multiprocessing](https://docs.python.org/3/library/multiprocessing.html)
- [JSON Configuration](https://docs.python.org/3/library/json.html)

## Конфигурационный файл
```json
{
  "staff_detection": {
    "min_line_length": 100,
    "max_line_gap": 20,
    "min_staff_height": 50
  },
  "symbol_detection": {
    "min_area": 100,
    "max_area": 5000,
    "padding": 5
  },
  "classifier": {
    "model_path": "../models/classifier_cnn.pth",
    "confidence_threshold": 0.8,
    "input_size": [64, 64]
  },
  "xml_export": {
    "title": "Detected Music",
    "author": "Music Symbols Detector",
    "default_key": "C",
    "default_time": "4/4"
  },
  "logging": {
    "level": "INFO",
    "file": "pipeline.log",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  },
  "temp_dir": "./temp",
  "cleanup_temp": true
}
```

## Ожидаемые результаты
- **Время обработки:** < 30 секунд на изображение A4
- **Точность:** > 85% правильно распознанных символов
- **Надежность:** работа без крашей
- **Масштабируемость:** обработка больших файлов 